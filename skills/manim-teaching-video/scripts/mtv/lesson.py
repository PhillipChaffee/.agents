"""Read, write, check and walk lesson.json, the single state file of a run."""

from __future__ import annotations

import keyword
import math
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from . import common

_KIND_NAMES = {str: "a string", list: "a list", dict: "an object"}


def load(path: Path) -> dict:
    """Read a lesson, giving every beat whose ``tail_s`` is absent or null its default hold."""
    lesson = common.load_json(path)
    for scene, beat in beats(lesson):
        if beat.get("tail_s") is None:
            beat["tail_s"] = common.LAST_TAIL_S if beat is scene["beats"][-1] else common.DEFAULT_TAIL_S
    return lesson


def save(lesson: dict, path: Path) -> None:
    common.dump_json(lesson, path)


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
