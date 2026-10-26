"""Vocabularies, constants and helpers shared by every manim-teaching-video script."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from num2words import num2words as _num2words
except ImportError:
    _num2words = None

MOVES: tuple[str, ...] = ("hook", "concrete", "abstraction", "formula", "recap", "aside", "meta", "outro")

SCENE_KINDS_CORPUS: tuple[str, ...] = (
    "spine",
    "support",
    "overlay",
    "ambient",
    "thumbnail",
    "end_screen",
    "stub",
    "utility",
)

TECHNIQUE_TAGS: frozenset[str] = frozenset(
    {
        "working-thing-first",
        "preview-then-hide",
        "zoom-to-one-unit",
        "numbers-before-symbols",
        "provenance-transform",
        "admit-uncertainty",
        "knobs-tremor",
        "light-the-path",
        "one-color-per-role",
        "object-budget",
        "montage-scale",
        "viewer-voice",
        "carry-picture-forward",
        "seeded-randomness",
        "save-and-restore",
        "caption-next-to-referent",
        "dim-not-delete",
        "parameter-count",
        "camera-as-narrator",
        "real-data-where-cheap",
        "honest-lie",
        "one-then-all",
        "pipeline-stays-on-screen",
        "micro-timing-in-one-play",
        "motion-with-a-reason",
        "transitions-reuse-geometry",
        "recurring-cast",
        "staggered-reveal",
    }
)

# ManimGL idiom found by the corpus census, mapped to the technique it signals.
IDIOM_TAGS: dict[str, str] = {
    "ReplacementTransform": "provenance-transform",
    "TransformFromCopy": "provenance-transform",
    "LaggedStartMap": "staggered-reveal",
    "LaggedStart": "staggered-reveal",
    "reorient": "camera-as-narrator",
    "frame.animate": "camera-as-narrator",
    "set_opacity": "dim-not-delete",
    "save_state": "save-and-restore",
    "Restore": "save-and-restore",
    "DecimalNumber": "numbers-before-symbols",
    "ShowPassingFlash": "light-the-path",
    "VShowPassingFlash": "light-the-path",
    "random.seed": "seeded-randomness",
}

# One key per patterns.py helper.
PATTERN_TAGS: dict[str, tuple[str, ...]] = {
    "LayeredNetwork": ("pipeline-stays-on-screen", "recurring-cast"),
    "NumericColumn": ("numbers-before-symbols",),
    "WeightGrid": ("numbers-before-symbols", "zoom-to-one-unit"),
    "provenance": ("provenance-transform", "transitions-reuse-geometry"),
    "numbers_to_symbol": ("numbers-before-symbols", "provenance-transform"),
    "save_and_restore_layout": ("save-and-restore",),
    "flash_along": ("light-the-path", "motion-with-a-reason"),
    "focus_and_dim": ("dim-not-delete", "one-then-all"),
    "nudge_and_return": ("knobs-tremor",),
    "count_parameters": ("parameter-count", "staggered-reveal"),
    "live_decimal": ("numbers-before-symbols", "knobs-tremor"),
    "zoom_to": ("zoom-to-one-unit", "camera-as-narrator"),
    "orbit_with_hud": ("camera-as-narrator", "motion-with-a-reason"),
    "staggered": ("staggered-reveal", "one-then-all"),
    "delayed": ("micro-timing-in-one-play",),
    "question_caption": ("viewer-voice", "caption-next-to-referent"),
}

MOVE_TAGS: dict[str, str] = {
    "hook": "working-thing-first",
    "recap": "carry-picture-forward",
    "formula": "numbers-before-symbols",
    "concrete": "one-then-all",
    "abstraction": "provenance-transform",
    "aside": "admit-uncertainty",
    "meta": "preview-then-hide",
    "outro": "carry-picture-forward",
}

RUNTIME_SCENE_KINDS: tuple[str, ...] = ("flat", "camera", "3d")
OPENING_STATES: tuple[str, ...] = ("black", "continue", "cut")

# A corpus exemplar id is an 11-character YouTube video id, then section and beat.
CORPUS_EXEMPLAR_ID = re.compile(r"\b[A-Za-z0-9_-]{11}-s\d{2}-b\d{2}\b")
ORIGINAL_EXEMPLAR_ID = re.compile(r"\borig-[a-z0-9-]+-s\d{2}-b\d{2}\b")

_SHADED_FAMILIES = ("BLUE", "TEAL", "GREEN", "YELLOW", "GOLD", "RED", "MAROON", "PURPLE", "GREY", "GRAY")

# Every ManimColor constant of CE manim/utils/color/manim_colors.py:129-220.
COLOR_NAMES: frozenset[str] = frozenset(
    _SHADED_FAMILIES
    + tuple(f"{family}_{shade}" for family in _SHADED_FAMILIES for shade in "ABCDE")
    + ("WHITE", "BLACK")
    + ("LIGHTER_GREY", "LIGHTER_GRAY", "LIGHT_GREY", "LIGHT_GRAY")
    + ("DARK_GREY", "DARK_GRAY", "DARKER_GREY", "DARKER_GRAY")
    + ("PURE_RED", "PURE_GREEN", "PURE_BLUE", "PURE_CYAN", "PURE_MAGENTA", "PURE_YELLOW")
    + ("DARK_BLUE", "PINK", "LIGHT_PINK", "ORANGE", "LIGHT_BROWN", "DARK_BROWN", "GREY_BROWN", "GRAY_BROWN")
    + ("LOGO_WHITE", "LOGO_GREEN", "LOGO_BLUE", "LOGO_RED", "LOGO_BLACK")
)

# Carry no role, so a scene may use them beside the lesson's color contract.
NEUTRAL_COLORS: frozenset[str] = frozenset(
    ("WHITE", "BLACK", "GREY", "GRAY")
    + tuple(f"{family}_{shade}" for family in ("GREY", "GRAY") for shade in "ABCDE")
    + ("LIGHT_GREY", "LIGHT_GRAY", "DARK_GREY", "DARK_GRAY")
    + ("LIGHTER_GREY", "LIGHTER_GRAY", "DARKER_GREY", "DARKER_GRAY")
)

DEFAULT_TAIL_S = 0.4
LAST_TAIL_S = 1.0
DEFAULT_LEAD_S = 0.2
OVERRUN_MAX_S = 1.0
SYNC_BEAT_TOLERANCE_S = 0.25  # pre-M0 default; set by M0 Task 9, copied in by Task 23
SYNC_CONTAINER_TOLERANCE_S = 0.5  # pre-M0 default; set by M0 Task 9, copied in by Task 23
HANG_TIMEOUT_S = 600  # pre-M0 default; set by M0 Task 9, copied in by Task 23
STANDARD_TO_DRAFT_RATIO = 10.1  # pre-M0 default; set by M0 Task 9, copied in by Task 23
CONTINUITY_THRESHOLD = 0.15  # pre-M1 default; recalibrated by Task 22

WORDS_PER_MINUTE = 150
R08_MAX_WORDS = 60
R09_MINUTES_PER_QUESTION = 2
R11_FIRST_FORMULA_FRACTION = 0.45  # pre-M2 default; replaced from the corpus census by the task the M2 plan names
ROLE_COLORS = {  # pre-M2 default; replaced from the corpus census by the task the M2 plan names
    "weight_pos": "BLUE",
    "weight_neg": "RED",
    "bias": "MAROON_B",
    "cost": "RED",
    "emphasis": "PURE_YELLOW",
}

# CE's default frame (manim/_config/utils.py:683-688): height 8.0, width the height
# times the 16:9 aspect of both tiers.
FRAME_WIDTH = 14.222222222222221
FRAME_HEIGHT = 8.0

TIERS = {"draft": (854, 480, 15), "standard": (1920, 1080, 30)}

LESSON_SCHEMA = "mtv-lesson/1"
EXEMPLARS_SCHEMA = "mtv-exemplars/1"
CONTINUITY_SCHEMA = "mtv-continuity/1"

_WORD_RUN = re.compile(r"[^\W_]+")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def normalize_words(text: str) -> list[str]:
    """Lower-case words of ``text``; anything but a letter or digit separates words.

    A numeral becomes its spoken words when ``num2words`` is installed, so a script's
    "784" lines up with the "seven hundred and eighty four" a narrator says.
    """
    words: list[str] = []
    for token in _WORD_RUN.findall(text.lower()):
        if token.isdecimal() and _num2words is not None:
            words.extend(normalize_words(_num2words(int(token))))
        else:
            words.append(token)
    return words


def thirteen_word_runs(text: str) -> set[str]:
    words = normalize_words(text)
    return {" ".join(words[i : i + 13]) for i in range(len(words) - 12)}


def load_json(path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(obj, path) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def lesson_parser(description: str, positional: bool = True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    if positional:
        parser.add_argument("lesson", type=Path, help="path to lesson.json")
    return parser


def verdict(ok: bool, text: str) -> int:
    print(f"{'PASS' if ok else 'FAIL'} {text}")
    return 0 if ok else 1


def usage_error(text: str) -> int:
    print(f"ERROR {text}", file=sys.stderr)
    return 2


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cmd(
    argv: list[str],
    log_path: Path | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=cwd, check=False)
    if log_path is not None:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(completed.stdout)
            log.write(completed.stderr)
    return completed


def ffprobe_json(path: Path) -> dict:
    completed = run_cmd(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    completed.check_returncode()
    return json.loads(completed.stdout)


def which(tool: str) -> str | None:
    return shutil.which(tool)


def load_valid_lesson(path: Path) -> tuple[dict, list[str]]:
    """Load and validate a lesson; an unreadable file is an error entry, not an exception.

    Every script exits 2 on the returned errors, and an uncaught exception would exit 1,
    the code that means a failed gate.
    """
    # Imported here because lesson.py imports this module at its top.
    from . import lesson as lesson_module

    try:
        lesson = lesson_module.load(path)
    except OSError as exc:
        return {}, [f"cannot read {path}: {exc.strerror or exc}"]
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {}, [f"cannot read {path}: {exc}"]
    return lesson, lesson_module.validate(lesson)
