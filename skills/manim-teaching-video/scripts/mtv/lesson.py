"""Read, write, check and walk lesson.json, the single state file of a run.

A run resumes from the same file: each finished stage records a hash of the fields it read,
and a stage whose fields have changed since then runs again.
"""

from __future__ import annotations

import json
import keyword
import math
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from . import common

_KIND_NAMES = {str: "a string", list: "a list", dict: "an object"}

# Pipeline order: a resumed run starts again at the first stage whose inputs have changed.
STAGES: tuple[str, ...] = (
    "brief", "script", "storyboard", "narrate", "scenes",
    "render.draft", "frames", "render.standard", "assemble", "verify",
)

# The digest of the generated lesson.py beside lesson.json, which load adds to the lesson and
# save leaves out, so it is never part of the file. The fix loop edits only that file, and every
# stage from render.draft on reads it, so it stands among their fields: a resume then renders
# an edit that a run stopped before rendering, or whose render failed.
SCENES_FILE_SHA256 = "lesson_py_sha256"

# The dotted fields each stage reads; "scenes[].x" is the field of every scene and "beats[].x"
# that of every beat. An entry naming a stage stands for all of that stage's fields, so a field
# added to an early stage reaches every later stage's hash without being copied into each row.
# A row may also name a field its parent stage already holds (scenes repeats seed, assemble
# repeats tier, both from brief); _expand keeps each field once, so a repeat changes no hash.
_STAGE_READS: dict[str, tuple[str, ...]] = {
    "brief": (
        "schema", "slug", "title", "audience", "target_minutes", "tier", "provider", "voice", "seed",
        "colors", "exemplars.dir", "exemplars.index_sha256",
    ),
    "script": ("brief", "scenes[].id", "scenes[].title", "beats[].id", "beats[].narration"),
    "storyboard": (
        "script", "scenes[].scene_class", "scenes[].scene_kind", "scenes[].opening_state",
        "scenes[].closing_state", "beats[].marks", "beats[].visual", "beats[].patterns", "beats[].moves",
        "beats[].introduces", "beats[].shows_value_of", "beats[].symbol_introduced", "beats[].lands",
        "beats[].tail_s",
    ),
    "narrate": ("provider", "voice", "beats[].id", "beats[].narration", "beats[].marks"),
    "scenes": ("storyboard", "seed"),
    "render.draft": ("scenes", SCENES_FILE_SHA256, "beats[].audio", "beats[].duration_s", "beats[].marks_s"),
    "frames": ("render.draft",),
    # Both renders read the same fields; which tier to render comes from the command line.
    "render.standard": ("render.draft",),
    "assemble": ("render.draft", "tier"),
    "verify": ("assemble",),
}


def _expand(stage: str) -> tuple[str, ...]:
    fields: list[str] = []
    for name in _STAGE_READS[stage]:
        fields.extend(_expand(name) if name in _STAGE_READS else (name,))
    return tuple(dict.fromkeys(fields))


STAGE_FIELDS: dict[str, tuple[str, ...]] = {stage: _expand(stage) for stage in STAGES}


def scenes_file(lesson_path: Path) -> Path:
    """The generated lesson.py: no CLI names it, so it is the file the run directory layout puts
    beside lesson.json."""
    return Path(lesson_path).resolve().parent / "lesson.py"


def load(path: Path) -> dict:
    """Read a lesson, giving every beat whose ``tail_s`` is absent or null its default hold and
    the lesson its ``SCENES_FILE_SHA256``, None when no generated lesson.py is beside it."""
    lesson = common.load_json(path)
    for scene, beat in beats(lesson):
        if beat.get("tail_s") is None:
            beat["tail_s"] = common.LAST_TAIL_S if beat is scene["beats"][-1] else common.DEFAULT_TAIL_S
    if isinstance(lesson, dict):
        scenes_py = scenes_file(path)
        lesson[SCENES_FILE_SHA256] = common.sha256_file(scenes_py) if scenes_py.is_file() else None
    return lesson


def save(lesson: dict, path: Path) -> None:
    common.dump_json({key: value for key, value in lesson.items() if key != SCENES_FILE_SHA256}, path)


def beats(lesson: dict) -> Iterator[tuple[dict, dict]]:
    for scene in _objects(lesson, "scenes"):
        for beat in _objects(scene, "beats"):
            yield scene, beat


def scene_by_id(lesson: dict, scene_id: str) -> dict:
    for scene in _objects(lesson, "scenes"):
        if scene.get("id") == scene_id:
            return scene
    raise KeyError(scene_id)


def beat_index(lesson: dict) -> dict[str, tuple[dict, dict]]:
    return {beat["id"]: (scene, beat) for scene, beat in beats(lesson)}


def unrendered(lesson: dict, run_dir: Path, tier: str) -> list[str]:
    """Each scene without beats and each beat without a video of this tier on disk."""
    scenes = lesson.get("scenes") or []
    problems = [] if scenes else ["no scenes"]
    problems += [f"{scene['id']}: no beats" for scene in scenes if not scene.get("beats")]
    for _, beat in beats(lesson):
        render = beat.get("render") or {}
        video = render.get("video")
        if not (
            isinstance(video, str)
            and Path(video).parts[:2] == ("render", tier)
            and (run_dir / video).is_file()
            and isinstance(render.get("duration_s"), (int, float))
        ):
            problems.append(f"{beat['id']}: no {tier} render.video")
    return problems


def validate(lesson: dict) -> list[str]:
    """Every schema violation in ``lesson``, in document order; empty when it is valid.

    Only schema, seed, the scene and beat ids and narration are required, because the brief
    and script stages validate a lesson that has no scenes or no storyboard fields yet; every
    other rule applies once its field is present. A malformed lesson yields errors, never an
    exception, so a bad file reads as invalid input rather than as a crash.
    """
    if not isinstance(lesson, dict):
        return ["lesson must be an object"]
    errors: list[str] = []
    if _has(errors, "", lesson, "schema") and lesson["schema"] != common.LESSON_SCHEMA:
        errors.append(f"schema is '{lesson['schema']}', expected '{common.LESSON_SCHEMA}'")
    if _has(errors, "", lesson, "seed") and not _is_int(lesson["seed"]):
        errors.append("seed must be an integer")
    provider, voice = lesson.get("provider"), lesson.get("voice")
    if isinstance(provider, str) and isinstance(voice, str) and not common.voice_suits(provider, voice):
        errors.append(f"voice '{voice}' is not a {provider} voice")
    for role, value in (_typed(errors, "", lesson, "colors", dict) or {}).items():
        if not (isinstance(value, str) and value in common.COLOR_NAMES):
            errors.append(f"colors['{role}'] = '{value}' is not a ManimCE color name")
    beat_ids: set[str] = set()
    for i, scene in enumerate(_typed(errors, "", lesson, "scenes", list) or []):
        errors.extend(_scene_errors(scene, f"scenes[{i}]", beat_ids))
    return errors


def _scene_errors(scene: Any, path: str, beat_ids: set[str]) -> list[str]:
    if not isinstance(scene, dict):
        return [f"{path} must be an object"]
    errors: list[str] = []
    scene_id = _typed(errors, path, scene, "id", str, required=True)
    owner = scene_id or path
    for name, allowed, vocabulary in (
        ("scene_kind", common.RUNTIME_SCENE_KINDS, "RUNTIME_SCENE_KINDS"),
        ("opening_state", common.OPENING_STATES, "OPENING_STATES"),
    ):
        if name in scene and scene[name] not in allowed:
            errors.append(f"{owner}: {name} '{scene[name]}' not in {vocabulary}")
    if "scene_class" in scene and not _is_identifier(scene["scene_class"]):
        errors.append(f"{owner}: scene_class '{scene['scene_class']}' is not a Python identifier")
    for j, beat in enumerate(_typed(errors, owner, scene, "beats", list) or []):
        errors.extend(_beat_errors(beat, scene_id, f"{path}.beats[{j}]", beat_ids))
    return errors


def _beat_errors(beat: Any, scene_id: str | None, path: str, beat_ids: set[str]) -> list[str]:
    if not isinstance(beat, dict):
        return [f"{path} must be an object"]
    errors: list[str] = []
    beat_id = _typed(errors, path, beat, "id", str, required=True)
    owner = beat_id or path
    if beat_id is not None:
        if scene_id is not None and not re.fullmatch(re.escape(scene_id) + r"-b\d{2}", beat_id):
            errors.append(f"{owner}: id does not match {scene_id}-bNN")
        if beat_id in beat_ids:
            errors.append(f"{owner}: duplicate beat id")
        beat_ids.add(beat_id)
    narration = _typed(errors, owner, beat, "narration", str, required=True)
    # Mark indices count these words and narration timing divides the audio among them,
    # so a beat with no words is rejected here instead of dividing by zero later.
    words = common.normalize_words(narration or "")
    if narration is not None and not words:
        errors.append(f"{owner}: narration has no words")
    for value in _typed(errors, owner, beat, "moves", list) or []:
        if value not in common.MOVES:
            errors.append(f"{owner}: moves value '{value}' not in MOVES")
    for value in _typed(errors, owner, beat, "patterns", list) or []:
        if not (isinstance(value, str) and value in common.PATTERN_TAGS):
            errors.append(f"{owner}: patterns value '{value}' not a PATTERN_TAGS key")
    marks = _typed(errors, owner, beat, "marks", dict) or {}
    for name, index in marks.items():
        if not (_is_int(index) and 0 <= index < len(words)):
            errors.append(f"{owner}: marks['{name}'] = {index!r} past the word count {len(words)}")
    for k, land in enumerate(_typed(errors, owner, beat, "lands", list) or []):
        if not isinstance(land, dict):
            errors.append(f"{owner}: lands[{k}] must be an object")
        elif not (isinstance(land.get("mark"), str) and land["mark"] in marks):
            errors.append(f"{owner}: lands mark '{land.get('mark')}' not in marks")
    if "tail_s" in beat and not _is_non_negative_number(beat["tail_s"]):
        errors.append(f"{owner}: tail_s must be a non-negative number")
    return errors


def stage_inputs(lesson: dict, stage: str) -> str:
    """sha256 of the fields ``stage`` reads (``STAGE_FIELDS``); KeyError for an unknown stage."""
    projection = {field: _read(lesson, _path(field)) for field in STAGE_FIELDS[stage]}
    return common.sha256_text(json.dumps(projection, sort_keys=True))


def needs_rerun(lesson: dict, stage: str) -> bool:
    # The hash comes first so that a mistyped stage raises instead of reading as never done.
    current = stage_inputs(lesson, stage)
    return lesson.get("stages", {}).get(stage, {}).get("inputs_sha256") != current


def mark_done(lesson: dict, stage: str, tools: dict[str, str]) -> None:
    lesson.setdefault("stages", {})[stage] = {
        "inputs_sha256": stage_inputs(lesson, stage),
        "done": common.now_iso(),
        "tools": tools,
    }


def bump(lesson: dict, counter: str, key: str | None = None) -> int:
    """Add one to ``attempts[counter]``, or to ``attempts[counter][key]``, counting an absent one as 0."""
    attempts = lesson.setdefault("attempts", {})
    counts, name = (attempts, counter) if key is None else (attempts.setdefault(counter, {}), key)
    counts[name] = counts.get(name, 0) + 1
    return counts[name]


def _read(value: Any, path: list[str]) -> Any:
    """What ``path`` reaches in ``value``, with one list for each ``[]`` step.

    needs_rerun is asked about stages whose fields no stage has written yet, so an absent
    field reads as None and an absent list as empty instead of raising.
    """
    if not path:
        return value
    key, rest = path[0], path[1:]
    if key.endswith("[]"):
        return [_read(item, rest) for item in _objects(value, key[:-2])]
    return _read(value.get(key) if isinstance(value, dict) else None, rest)


def _path(field: str) -> list[str]:
    # STAGE_FIELDS writes "beats[].x" for the beats of every scene.
    steps = field.split(".")
    return ["scenes[]", *steps] if steps[0] == "beats[]" else steps


def _objects(container: Any, key: str) -> list[dict]:
    # load fills defaults before validate has run, so a missing or malformed field
    # yields nothing here and validate reports it.
    value = container.get(key) if isinstance(container, dict) else None
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _has(errors: list[str], owner: str, obj: dict, name: str) -> bool:
    if name in obj:
        return True
    errors.append(_at(owner, f"missing field '{name}'"))
    return False


def _typed(errors: list[str], owner: str, obj: dict, name: str, kind: type, required: bool = False) -> Any:
    """``obj[name]`` when it has type ``kind``, else None after recording why."""
    if not (_has(errors, owner, obj, name) if required else name in obj):
        return None
    if isinstance(obj[name], kind):
        return obj[name]
    errors.append(_at(owner, f"{name} must be {_KIND_NAMES[kind]}"))
    return None


def _at(owner: str, text: str) -> str:
    # Top-level errors carry no owner, matching "seed must be an integer".
    return f"{owner}: {text}" if owner else text


def _is_int(value: Any) -> bool:
    # bool subclasses int, and JSON true is neither a seed nor a word index.
    return isinstance(value, int) and not isinstance(value, bool)


def _is_identifier(value: Any) -> bool:
    # A keyword passes isidentifier() but cannot name a class.
    return isinstance(value, str) and value.isidentifier() and not keyword.iskeyword(value)


def _is_non_negative_number(value: Any) -> bool:
    return (_is_int(value) or (isinstance(value, float) and math.isfinite(value))) and value >= 0
