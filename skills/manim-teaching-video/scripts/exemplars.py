"""Check an exemplar pack, and pick the exemplars a storyboarder or a frame critic is shown.

A pack is optional and lives outside the kit, in the directory ``MTV_EXEMPLARS`` names:
``index.json`` plus one contact sheet and one excerpt per exemplar. ``pick`` refuses a pack
that fails ``check``, because a run without a valid pack goes on without exemplars.
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from mtv import common
from mtv import lesson as mtv_lesson

# In priority order: a smaller --max-images keeps the first tags.
STORYBOARDER_TAGS = (
    "working-thing-first",
    "numbers-before-symbols",
    "provenance-transform",
    "viewer-voice",
    "carry-picture-forward",
    "dim-not-delete",
    "staggered-reveal",
    "camera-as-narrator",
)
CORPUS_FIELDS = ("video_id", "section_id", "beat_id", "t_start", "t_end")
ORIGINAL_FIELDS = ("lesson_slug", "scene_id", "beat_id", "helpers", "report")
COMMON_FIELDS = ("id", "source", "tiles", "sheet", "excerpt", "rule_ids", "gist", "confidence")

_SOURCES = {
    "corpus": (CORPUS_FIELDS, common.CORPUS_EXEMPLAR_ID),
    "original": (ORIGINAL_FIELDS, common.ORIGINAL_EXEMPLAR_ID),
}
MAX_SHEET_WIDTH, MAX_SHEET_HEIGHT = 1280, 480
MIN_TILES, MAX_TILES = 2, 6
# Only a lesson that moves its camera needs an exemplar of a camera move.
_CAMERA_SCENE_KINDS = ("camera", "3d")

# Baseline and progressive frame headers, the two in common use.
_SOF_MARKERS = (0xC0, 0xC2)
# TEM and RST0 to RST7 carry no length field.
_STANDALONE_MARKERS = frozenset((0x01, *range(0xD0, 0xD8)))
# Start of scan and end of image: no frame header can follow either.
_SOS, _EOI = 0xDA, 0xD9


def jpeg_size(path: Path) -> tuple[int, int]:
    """``(width, height)`` from the first SOF0 or SOF2 frame header; ValueError for anything else."""
    data = Path(path).read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError(f"{path} is not a JPEG")
    offset = 2
    try:
        while data[offset] == 0xFF:
            # Any number of 0xFF fill bytes may precede a marker.
            while data[offset] == 0xFF:
                offset += 1
            marker = data[offset]
            offset += 1
            if marker in (_SOS, _EOI):
                break
            if marker in _STANDALONE_MARKERS:
                continue
            if marker in _SOF_MARKERS:
                # After the length and the sample precision, the line count, then samples per line.
                height, width = struct.unpack_from(">HH", data, offset + 3)
                return width, height
            offset += struct.unpack_from(">H", data, offset)[0]
    except (IndexError, struct.error):
        pass
    raise ValueError(f"{path} has no SOF0 or SOF2 frame header")


def check(pack_dir: Path) -> list[str]:
    """Every way the pack breaks the ``mtv-exemplars/1`` contract, each ``<owner>: <text>``.

    A malformed index yields findings, never an exception, because a broken pack is a
    warning and never a stop.
    """
    pack_dir = Path(pack_dir)
    index_path = pack_dir / "index.json"
    if not index_path.is_file():
        return ["index.json missing"]
    try:
        index = common.load_json(index_path)
    except (OSError, ValueError) as exc:
        return [f"index.json: cannot read: {exc}"]
    if not isinstance(index, dict):
        return ["index.json: must be an object"]
    findings = []
    if index.get("schema") != common.EXEMPLARS_SCHEMA:
        findings.append(f"index.json: schema is '{index.get('schema')}', expected '{common.EXEMPLARS_SCHEMA}'")
    tags = index.get("tags")
    if not isinstance(tags, dict):
        return [*findings, "index.json: tags must be an object"]
    for tag, entries in tags.items():
        if tag not in common.TECHNIQUE_TAGS:
            findings.append(f"{tag}: tag '{tag}' not in TECHNIQUE_TAGS")
        if not isinstance(entries, list):
            findings.append(f"{tag}: entries must be a list")
            continue
        for i, entry in enumerate(entries):
            findings.extend(_entry_findings(entry, f"{tag}[{i}]", pack_dir))
    return findings


def _entry_findings(entry: Any, position: str, pack_dir: Path) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{position}: entry must be an object"]
    source = entry.get("source")
    # A JSON list or object is unhashable, and a lookup with it would raise instead of finding.
    fields, id_pattern = _SOURCES.get(source, ((), None)) if isinstance(source, str) else ((), None)
    texts = [f"missing field '{field}'" for field in COMMON_FIELDS + fields if field not in entry]
    if "source" in entry and id_pattern is None:
        texts.append(f"source '{source}' is not corpus or original")
    if id_pattern is not None and "id" in entry and not (
        isinstance(entry["id"], str) and id_pattern.fullmatch(entry["id"])
    ):
        texts.append(f"id does not match the {source} pattern")
    for name in ("sheet", "excerpt"):
        if name in entry and not _is_pack_file(pack_dir, entry[name]):
            texts.append(f"{name} '{entry[name]}' missing")
    if _is_pack_file(pack_dir, entry.get("sheet")):
        try:
            width, height = jpeg_size(pack_dir / entry["sheet"])
        except ValueError:
            texts.append(f"sheet '{entry['sheet']}' is not a JPEG")
        else:
            if width > MAX_SHEET_WIDTH or height > MAX_SHEET_HEIGHT:
                texts.append(f"sheet {width}x{height} larger than {MAX_SHEET_WIDTH}x{MAX_SHEET_HEIGHT}")
    if "tiles" in entry and not _in_range(entry["tiles"], MIN_TILES, MAX_TILES, (int,)):
        texts.append(f"tiles {entry['tiles']} outside {MIN_TILES} to {MAX_TILES}")
    if "confidence" in entry and not _in_range(entry["confidence"], 0, 1, (int, float)):
        texts.append(f"confidence {entry['confidence']} outside 0 to 1")
    owner = entry["id"] if isinstance(entry.get("id"), str) else position
    return [f"{owner}: {text}" for text in texts]


def _is_pack_file(pack_dir: Path, relative: Any) -> bool:
    return isinstance(relative, str) and (pack_dir / relative).is_file()


def _in_range(value: Any, low: float, high: float, kinds: tuple[type, ...]) -> bool:
    # bool subclasses int, and JSON true is neither a tile count nor a confidence.
    return isinstance(value, kinds) and not isinstance(value, bool) and low <= value <= high


def pick_storyboarder(
    index: dict, lesson: dict, pack_dir: Path, max_images: int = 8, max_words: int = 1000
) -> list[dict]:
    """The best exemplar of each ``STORYBOARDER_TAGS`` tag the pack holds, in that order."""
    camera = any(scene.get("scene_kind") in _CAMERA_SCENE_KINDS for scene in lesson.get("scenes", []))
    tags = [tag for tag in STORYBOARDER_TAGS if camera or tag != "camera-as-narrator"]
    return _within_budget(_best_per_tag(index, tags), pack_dir, max_images, max_words)


def pick_frame_critic(
    index: dict, lesson: dict, scene_id: str, pack_dir: Path, max_images: int = 4, max_words: int = 500
) -> list[dict]:
    """The best exemplar of each tag the scene's beats reach through their patterns and moves,
    most confident first; KeyError for an unknown scene."""
    tags: set[str] = set()
    for beat in mtv_lesson.scene_by_id(lesson, scene_id).get("beats", []):
        for pattern in beat.get("patterns", []):
            tags.update(common.PATTERN_TAGS[pattern])
        tags.update(common.MOVE_TAGS[move] for move in beat.get("moves", []))
    # No reached tag outranks another, so confidence decides which survive max_images. The tags
    # are sorted first because set order varies between runs and one entry can serve two tags.
    best = sorted(_best_per_tag(index, sorted(tags)), key=lambda pair: _rank(pair[1]))
    return _within_budget(best, pack_dir, max_images, max_words)


def _rank(entry: dict) -> tuple[float, str]:
    return -entry["confidence"], entry["id"]


def _best_per_tag(index: dict, tags: Iterable[str]) -> list[tuple[str, dict]]:
    """Each tag's most confident entry, ties by id, for the tags the pack holds."""
    return [(tag, min(index["tags"][tag], key=_rank)) for tag in tags if index["tags"].get(tag)]


def _within_budget(best: list[tuple[str, dict]], pack_dir: Path, max_images: int, max_words: int) -> list[dict]:
    """The first ``max_images`` picks; ``words`` is how many leading words of its excerpt each
    shows, so the excerpts shrink to fit ``max_words`` while every sheet stays."""
    kept = best[:max_images]
    lengths = [len((pack_dir / entry["excerpt"]).read_text(encoding="utf-8").split()) for _, entry in kept]
    return [
        {"id": entry["id"], "tag": tag, "sheet": entry["sheet"], "excerpt": entry["excerpt"], "words": words}
        for (tag, entry), words in zip(kept, _fair_shares(lengths, max_words))
    ]


def _fair_shares(lengths: list[int], budget: int) -> list[int]:
    """Each length capped at the largest equal share that keeps the total within ``budget``.

    Cutting the longest excerpts first leaves every exemplar its opening lines, id included.
    """
    cap, remaining = max(lengths, default=0), budget
    for done, length in enumerate(sorted(lengths)):
        share = remaining // (len(lengths) - done)
        if length > share:
            cap = share
            break
        remaining -= length
    return [min(length, cap) for length in lengths]


def _pack_dir(configured: str | None) -> Path | None:
    value = configured or os.environ.get("MTV_EXEMPLARS")
    return Path(value) if value else None


def _count(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError(f"{text} is negative")
    return value


def _check_command(directory: str | None) -> int:
    pack_dir = _pack_dir(directory)
    if pack_dir is None:
        return common.usage_error("no pack directory given and MTV_EXEMPLARS is unset")
    findings = check(pack_dir)
    for finding in findings:
        print(finding)
    if findings:
        return common.verdict(False, f"{len(findings)} findings")
    index_path = pack_dir / "index.json"
    # The brief stage copies this hash into exemplars.index_sha256.
    print(f"index.json sha256 {common.sha256_file(index_path)}")
    tags = common.load_json(index_path)["tags"]
    return common.verdict(True, f"{sum(map(len, tags.values()))} exemplars under {len(tags)} tags")


def _pick_command(args: argparse.Namespace) -> int:
    if args.role == "frame-critic" and args.scene is None:
        return common.usage_error("--role frame-critic needs --scene")
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    if args.role == "frame-critic" and args.scene not in {scene["id"] for scene in lesson.get("scenes", [])}:
        return common.usage_error(f"no scene '{args.scene}' in {args.lesson}")
    exemplars = lesson.get("exemplars") or {}
    pack_dir = _pack_dir(exemplars.get("dir"))
    if pack_dir is None:
        return common.usage_error("no exemplar pack: exemplars.dir is null and MTV_EXEMPLARS is unset")
    findings = check(pack_dir)
    if findings:
        return common.usage_error(f"exemplar pack {pack_dir} fails check with {len(findings)} findings")
    index = common.load_json(pack_dir / "index.json")
    # Absent flags fall through to the role's budget, the defaults of its pick function.
    budget = {name: value for name, value in (("max_images", args.max_images), ("max_words", args.max_words))
              if value is not None}
    used = exemplars.setdefault("used", {})
    if args.role == "storyboarder":
        picks = pick_storyboarder(index, lesson, pack_dir, **budget)
        used["storyboarder"] = [pick["id"] for pick in picks]
    else:
        picks = pick_frame_critic(index, lesson, args.scene, pack_dir, **budget)
        used.setdefault("frame-critic", {})[args.scene] = [pick["id"] for pick in picks]
    lesson["exemplars"] = exemplars
    mtv_lesson.save(lesson, args.lesson)
    print(json.dumps(picks))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check an exemplar pack, or pick a role's exemplars from it.")
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check", help="validate a pack against the mtv-exemplars/1 contract")
    check_parser.add_argument("dir", nargs="?", help="pack directory; default $MTV_EXEMPLARS")
    pick_text = "pick the exemplars a role is shown and record them in exemplars.used"
    # The lesson parser is a parent, so pick takes lesson.json the way every lesson script does.
    pick_parser = commands.add_parser(
        "pick", parents=[common.lesson_parser(pick_text)], add_help=False, description=pick_text, help=pick_text
    )
    pick_parser.add_argument("--role", required=True, choices=("storyboarder", "frame-critic"))
    pick_parser.add_argument("--scene", help="the scene whose frame critic is shown the picks")
    pick_parser.add_argument("--max-images", type=_count, help="most picks; default 8, or 4 for the frame critic")
    pick_parser.add_argument("--max-words", type=_count, help="most excerpt words; default 1000, or 500")
    args = parser.parse_args(argv)
    return _check_command(args.dir) if args.command == "check" else _pick_command(args)


if __name__ == "__main__":
    sys.exit(main())
