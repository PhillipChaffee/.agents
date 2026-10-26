"""Check a lesson's script or storyboard against the framework rules its fields can show.

The full check also resolves every mark to a word and rejects exemplar ids copied into
the lesson; ``--script`` runs on a lesson that has narration but no storyboard fields yet,
so it checks only the word budget and the voice rules.
"""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Callable, Iterator
from typing import Any

from mtv import common
from mtv import lesson as mtv_lesson

VOICE_RULES = ("R08", "R09", "R10", "R11")
BUDGET_TOLERANCE = 0.15
MAX_SENTENCES = 3

# The short statements of the framework's rule table, quoted in each finding so the
# storyboarder sees which rule a beat breaks.
_STATEMENTS = {
    "R01": "a working thing before any definition",
    "R03": "a question is planted before its answer and held across at least one beat",
    "R06": "the lesson's picture is carried into the recap",
    "R07": "a quantity is shown as a number before its symbol; the symbol transforms from a copy of the number",
    "R08": f"a beat is 1 to {MAX_SENTENCES} sentences and at most {common.R08_MAX_WORDS} words",
    "R09": f"at least one question per {common.R09_MINUTES_PER_QUESTION} minutes of script",
    "R10": "second person or first person plural, never third person about the learner",
    "R11": "the first formula follows at least one concrete beat and arrives no later than the corpus"
    " first_formula_fraction plus 0.20 of the lesson",
    "R16": "scene boundaries are continuous or deliberately cleared",
    "R28": "at least one beat per lesson admits an uncertainty or names a simplification",
}

_SENTENCE_END = re.compile(r"[.!?]+")
_THIRD_PERSON = re.compile(r"\bthe (learner|student|viewer|reader)s?\b", re.IGNORECASE)
# lesson.validate's wording of the two mark errors, which this script reports as findings.
_MARK_ERROR = re.compile(r"[^:]+: (marks\[.*\] = .* past the word count \d+|lands mark .* not in marks)")


def _beats(lesson: dict) -> list[dict]:
    return [beat for _, beat in mtv_lesson.beats(lesson)]


def _list(item: dict, key: str) -> list:
    # lesson.validate checks the type of only some storyboard fields, and every one is optional.
    value = item.get(key)
    return value if isinstance(value, list) else []


def _word_count(beat: dict) -> int:
    return len(common.normalize_words(beat["narration"]))


def _introduces_anything(beat: dict) -> bool:
    return bool(_list(beat, "introduces") or _list(beat, "symbol_introduced"))


def _sentence_count(narration: str) -> int:
    return sum(1 for piece in _SENTENCE_END.split(narration) if piece.strip())


def _first_beat_if(beats: list[dict], failed: bool) -> list[str]:
    # A rule about a whole lesson or scene has no beat of its own, so its finding names the first one.
    return [beats[0]["id"]] if beats and failed else []


def _r01_hook_first(lesson: dict) -> list[str]:
    """The first beat's moves lack hook."""
    beats = _beats(lesson)
    return [beats[0]["id"]] if beats and "hook" not in _list(beats[0], "moves") else []


def _r03_question_held(lesson: dict) -> list[str]:
    """A beat ending in a question is the lesson's last beat or introduces something itself."""
    beats = _beats(lesson)
    return [
        beat["id"]
        for i, beat in enumerate(beats)
        if beat["narration"].rstrip().endswith("?") and (i == len(beats) - 1 or _introduces_anything(beat))
    ]


def _r06_recap_last(lesson: dict) -> list[str]:
    """The last scene has no recap beat, or a recap beat of it introduces something."""
    scenes = lesson.get("scenes", [])
    beats = scenes[-1].get("beats", []) if scenes else []
    recaps = [beat for beat in beats if "recap" in _list(beat, "moves")]
    return _first_beat_if(beats, not recaps) + [beat["id"] for beat in recaps if _introduces_anything(beat)]


def _r07_value_before_symbol(lesson: dict) -> list[str]:
    """A beat introduces a symbol whose value no strictly earlier beat shows."""
    failing, shown = [], []
    for beat in _beats(lesson):
        if any(symbol not in shown for symbol in _list(beat, "symbol_introduced")):
            failing.append(beat["id"])
        shown.extend(_list(beat, "shows_value_of"))
    return failing


def _r08_beat_length(lesson: dict) -> list[str]:
    """A beat has too many words, or too few or too many sentences."""
    return [
        beat["id"]
        for beat in _beats(lesson)
        if _word_count(beat) > common.R08_MAX_WORDS or not 1 <= _sentence_count(beat["narration"]) <= MAX_SENTENCES
    ]


def _r09_questions(lesson: dict) -> list[str]:
    """Fewer beats ask a question than the script's spoken minutes call for."""
    beats = _beats(lesson)
    minutes = sum(map(_word_count, beats)) / common.WORDS_PER_MINUTE
    needed = max(1, math.ceil(minutes / common.R09_MINUTES_PER_QUESTION))
    return _first_beat_if(beats, sum("?" in beat["narration"] for beat in beats) < needed)


def _r10_voice(lesson: dict) -> list[str]:
    """A beat's narration speaks of the learner in the third person."""
    return [beat["id"] for beat in _beats(lesson) if _THIRD_PERSON.search(beat["narration"])]


def _r11_first_formula(lesson: dict) -> list[str]:
    """The first formula beat has no concrete beat before it, or comes too late in the words."""
    beats = _beats(lesson)
    latest = (common.R11_FIRST_FORMULA_FRACTION + 0.20) * sum(map(_word_count, beats))
    words_before, concrete_before = 0, False
    for beat in beats:
        if "formula" in _list(beat, "moves") or _list(beat, "symbol_introduced"):
            return [beat["id"]] if words_before > latest or not concrete_before else []
        words_before += _word_count(beat)
        concrete_before = concrete_before or "concrete" in _list(beat, "moves")
    return []


def _r16_continuity(lesson: dict) -> list[str]:
    """A scene continues from no previous scene, or from one with no closing_state."""
    failing, previous = [], None
    for scene in lesson.get("scenes", []):
        closing = previous.get("closing_state") if previous else None
        unset = not (isinstance(closing, str) and closing.strip())
        failing.extend(_first_beat_if(scene.get("beats", []), scene.get("opening_state") == "continue" and unset))
        previous = scene
    return failing


def _r28_aside(lesson: dict) -> list[str]:
    """No beat carries aside."""
    beats = _beats(lesson)
    return _first_beat_if(beats, not any("aside" in _list(beat, "moves") for beat in beats))


PREDICATES: dict[str, Callable[[dict], list[str]]] = {
    "R01": _r01_hook_first,
    "R03": _r03_question_held,
    "R06": _r06_recap_last,
    "R07": _r07_value_before_symbol,
    "R08": _r08_beat_length,
    "R09": _r09_questions,
    "R10": _r10_voice,
    "R11": _r11_first_formula,
    "R16": _r16_continuity,
    "R28": _r28_aside,
}


def _finding(beat: str | None, rule_id: str | None, text: str) -> dict:
    return {"beat": beat, "rule_id": rule_id, "text": text}


def mark_findings(lesson: dict) -> list[dict]:
    findings = []
    for beat in _beats(lesson):
        marks, n_words = beat.get("marks", {}), _word_count(beat)
        # type() rather than isinstance, since JSON true is a bool and bool subclasses int.
        names = [name for name, index in marks.items() if not (type(index) is int and 0 <= index < n_words)]
        for land in _list(beat, "lands"):
            if not (isinstance(land.get("mark"), str) and land["mark"] in marks):
                names.append(land.get("mark"))
        findings.extend(_finding(beat["id"], None, f"mark '{name}' does not resolve to a word") for name in names)
    return findings


def _text_fields(beat: dict) -> Iterator[tuple[str, Any]]:
    yield "narration", beat.get("narration")
    yield "visual", beat.get("visual")
    for k, land in enumerate(_list(beat, "lands")):
        yield f"lands[{k}].visual", land.get("visual")
    for key in ("introduces", "shows_value_of", "symbol_introduced"):
        for k, entry in enumerate(_list(beat, key)):
            yield f"{key}[{k}]", entry


def _exemplar_id(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    # An original id can end in a corpus-shaped id, so its own pattern goes first and the
    # finding quotes the whole id.
    for pattern in (common.ORIGINAL_EXEMPLAR_ID, common.CORPUS_EXEMPLAR_ID):
        match = pattern.search(text)
        if match:
            return match.group()
    return None


def leak_findings(lesson: dict) -> list[dict]:
    findings = []
    for beat in _beats(lesson):
        for field, text in _text_fields(beat):
            leaked = _exemplar_id(text)
            if leaked is not None:
                findings.append(_finding(beat["id"], None, f"exemplar id '{leaked}' leaked into {field}"))
    return findings


def budget_findings(lesson: dict) -> list[dict]:
    words = sum(map(_word_count, _beats(lesson)))
    target = lesson["target_minutes"] * common.WORDS_PER_MINUTE
    low, high = target * (1 - BUDGET_TOLERANCE), target * (1 + BUDGET_TOLERANCE)
    if low <= words <= high:
        return []
    return [_finding(None, None, f"word budget {words} outside [{low:g}, {high:g}]")]


def run(lesson: dict, script_only: bool) -> list[dict]:
    if script_only:
        findings, rules = budget_findings(lesson), VOICE_RULES
    else:
        findings, rules = mark_findings(lesson) + leak_findings(lesson), tuple(PREDICATES)
    for rule_id in rules:
        text = f"{rule_id}: {_STATEMENTS[rule_id]}"
        findings.extend(_finding(beat_id, rule_id, text) for beat_id in PREDICATES[rule_id](lesson))
    return findings


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Check a lesson's storyboard, or with --script its script, against the framework.")
    parser.add_argument("--script", action="store_true", help="check only the word budget and the voice rules")
    args = parser.parse_args(argv)
    lesson, errors = common.load_valid_lesson(args.lesson)
    # An unresolved mark is a storyboard defect for this gate to report, not unreadable input.
    errors = [error for error in errors if not _MARK_ERROR.fullmatch(error)]
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    if args.script and not _is_positive_number(lesson.get("target_minutes")):
        return common.usage_error("--script needs target_minutes, a positive number")
    findings = run(lesson, args.script)
    lesson.setdefault("checks", {})["storyboard"] = {"pass": not findings, "at": common.now_iso(), "findings": findings}
    mtv_lesson.save(lesson, args.lesson)
    for finding in findings:
        print(f"{finding['beat'] or '-'} {finding['rule_id'] or '-'} {finding['text']}")
    return common.verdict(not findings, f"storyboard: {len(findings)} findings")


if __name__ == "__main__":
    sys.exit(main())
