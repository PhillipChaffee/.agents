"""Hold the assembled lesson to the hard gates, then write report.md.

Every gate is a fail: a lesson that fails one is never delivered. Each gate yields one row
of checks.verify, a per-beat gate the row of its worst beat, so the parent reads the whole
verdict from the checks block and the user reads it from report.md. With --external it runs
the subset that needs no lesson on any MP4, a video made without the skill included, and
writes nothing.
"""

from __future__ import annotations

import json
import math
import statistics
import subprocess
import sys
import wave
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import check_scenes
import frames
from mtv import common, tts
from mtv import lesson as mtv_lesson

MISSING = "missing"
UNREADABLE = "unreadable"
RUBRIC_MAX = 32  # sixteen items scored 0 to 2
SAMPLE_EVERY_S = 10
# 3b1b-style lessons sit on near-black backgrounds, so a frame mean under spec 6.12's 8 of 255 is
# normal: not black detects absent content, not darkness. The cut of 32 also clears the up-to-3
# that ffmpeg 6.1.1's bicubic scale reads for black. A narrated hold longer than SAMPLE_EVERY_S
# yields identical samples, so not frozen fails only a video that never changes.
LIT_LUMA = 32  # of 255: a pixel above this shows content
BLACK_LIT_SHARE = 0.01  # a frame with a smaller share of lit pixels is black
IDENTICAL_MAD = 0.01  # consecutive samples closer than this show the same picture


@dataclass
class GateResult:
    gate: str
    measured: float | str | None
    tolerance: float | None
    passed: bool

    def as_dict(self) -> dict:
        return {"gate": self.gate, "measured": self.measured, "tolerance": self.tolerance, "pass": self.passed}


def output_path(lesson: dict, run_dir: Path, tier: str) -> Path:
    return run_dir / "out" / f"{lesson['slug']}.{tier}.mp4"


def _dig(value: Any, *keys: str) -> Any:
    """``value[key][key]...``, or None where a step is absent or not an object."""
    for key in keys:
        value = value.get(key) if isinstance(value, dict) else None
    return value


def _number(value: Any) -> float | None:
    # bool subclasses int, and a JSON true is no measurement.
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _read_json(path: Path) -> Any:
    try:
        return common.load_json(path)
    except (OSError, ValueError):
        return None


def _probe(mp4: Path) -> dict | None:
    # The file exists (main checks), so a probe that fails means a file no player can read.
    try:
        return common.ffprobe_json(mp4)
    except (subprocess.CalledProcessError, ValueError):
        return None


def _seconds(value: Any) -> float | None:
    """An ffprobe duration, which is a string, or None where ffprobe could not tell one."""
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if math.isfinite(seconds) else None


def _container_s(mp4: Path) -> float | None:
    return _seconds(_dig(_probe(mp4), "format", "duration"))


def _within(gate: str, actual_s: float | None, expected_s: float | None, tolerance: float) -> GateResult:
    if actual_s is None or expected_s is None:
        return GateResult(gate, MISSING, tolerance, False)
    difference = round(abs(actual_s - expected_s), 6)
    return GateResult(gate, difference, tolerance, difference <= tolerance)


def _worst(gate: str, values: list[float | None], limit: float, tolerance: float | None) -> list[GateResult]:
    """The row of a per-beat gate: its worst beat's value, passing only when no beat exceeds
    ``limit``; a beat whose inputs are missing fails it."""
    if None in values:
        return [GateResult(gate, MISSING, tolerance, False)]
    worst = max(values, default=0.0)
    return [GateResult(gate, round(worst, 6), tolerance, worst <= limit)]


def _section_spans(run_dir: Path, tier: str, scene: dict) -> dict[str, tuple[float, float]] | None:
    """Each section's start and end in its scene's video, from the running sum of the durations
    in the scene's section index; None when the index is missing or unreadable.

    Every entry counts toward the sum, a non-beat one such as CE's autocreated first section
    included, because the scene's video plays all of them.
    """
    entries = _read_json(run_dir / "render" / tier / scene["id"] / "sections.json")
    spans, start_s = {}, 0.0
    try:
        for entry in entries:
            end_s = start_s + float(entry["duration"])
            spans[entry["name"]] = (start_s, end_s)
            start_s = end_s
    except (KeyError, TypeError, ValueError):
        return None
    return spans


def _run_log_span(beat: dict) -> tuple[float, float] | None:
    log = _dig(beat, "render", "log")
    enter_s, exit_s = _number(_dig(log, "enter_s")), _number(_dig(log, "exit_s"))
    return None if enter_s is None or exit_s is None else (enter_s, exit_s)


def _stream_row(probe: dict | None) -> GateResult:
    if probe is None:
        return GateResult("streams", UNREADABLE, None, False)
    kinds = sorted(str(stream.get("codec_type")) for stream in probe.get("streams", []))
    return GateResult("streams", ", ".join(kinds), None, kinds == ["audio", "video"])


def streams(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    return [_stream_row(_probe(output_path(lesson, run_dir, tier)))]


def container_duration(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    actual_s = _container_s(output_path(lesson, run_dir, tier))
    beats = [beat for _, beat in mtv_lesson.beats(lesson)]
    audio = [_number(beat.get("duration_s")) for beat in beats]
    expected_s = None if None in audio else sum(audio) + sum(beat["tail_s"] for beat in beats)
    return [_within("container duration", actual_s, expected_s, common.SYNC_CONTAINER_TOLERANCE_S)]


def run_log_vs_section_index(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    """Each beat's run-log entry and exit against where its section starts and ends."""
    deviations: list[float | None] = []
    for scene in lesson.get("scenes", []):
        spans = _section_spans(run_dir, tier, scene) or {}
        for beat in scene.get("beats", []):
            logged, indexed = _run_log_span(beat), spans.get(beat["id"])
            deviations.append(
                None if logged is None or indexed is None
                else max(abs(logged[0] - indexed[0]), abs(logged[1] - indexed[1]))
            )
    tolerance = common.SYNC_BEAT_TOLERANCE_S
    return _worst("run log vs section index", deviations, tolerance, tolerance)


def _wav_excess(beat: dict, run_dir: Path) -> float | None:
    """How much longer the beat's WAV is than its rendered video; negative when it is shorter."""
    rendered_s = _number(_dig(beat, "render", "duration_s"))
    try:
        audio_s = tts.wav_duration(run_dir / beat["audio"])
    except (KeyError, TypeError, OSError, EOFError, wave.Error):
        return None
    return None if rendered_s is None else audio_s - rendered_s


def wav_within_beat(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    excesses = [_wav_excess(beat, run_dir) for _, beat in mtv_lesson.beats(lesson)]
    return _worst("wav within beat", excesses, 0.0, 0.0)


def _marks_outside(beat: dict) -> float | None:
    """How far the beat's furthest mark lies outside the beat, 0 when every mark is inside.

    A mark time counts from the beat's start, so the beat spans 0 to its exit_s minus enter_s.
    """
    span = _run_log_span(beat)
    marks = [_number(t_s) for t_s in (beat.get("marks_s") or {}).values()]
    if span is None or None in marks:
        return None
    length_s = span[1] - span[0]
    return max((max(-t_s, t_s - length_s, 0.0) for t_s in marks), default=0.0)


def marks_inside_beat(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    return _worst("marks inside beat", [_marks_outside(beat) for _, beat in mtv_lesson.beats(lesson)], 0.0, None)


def overrun(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    overruns = [_number(_dig(beat, "render", "log", "overrun_s")) for _, beat in mtv_lesson.beats(lesson)]
    return _worst("overrun", overruns, common.OVERRUN_MAX_S, common.OVERRUN_MAX_S)


def banned_names(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    # check_scenes.py's own reading of the rule, so a word in a comment passes both alike;
    # scenes_file reads only the directory of the lesson path it is given.
    lesson_py = mtv_lesson.scenes_file(run_dir / "lesson.json")
    if not lesson_py.is_file():
        return [GateResult("banned names", MISSING, None, False)]
    count = len(check_scenes.banned_findings(lesson_py.read_text(encoding="utf-8", errors="replace")))
    return [GateResult("banned names", count, None, count == 0)]


def index_coverage(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    """The scenes without a section index and the beats without an entry in theirs."""
    missing = 0
    for scene in lesson.get("scenes", []):
        spans = _section_spans(run_dir, tier, scene)
        missing += 1 if spans is None else sum(beat["id"] not in spans for beat in scene.get("beats", []))
    return [GateResult("index coverage", missing, None, missing == 0)]


def latex_error(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    logs = sorted((run_dir / "render" / tier).glob("*/render.log"))
    failing = sum(common.LATEX_ERROR in log.read_text(encoding="utf-8", errors="replace") for log in logs)
    return [GateResult("latex error", failing, None, failing == 0)]


def continuity(lesson: dict, run_dir: Path, tier: str) -> list[GateResult]:
    """The worst jump into a scene that continues the previous one, judged by frames.py."""
    record = _read_json(run_dir / "frames" / "continuity.json")
    if not isinstance(record, dict):
        return [GateResult("continuity", MISSING, common.CONTINUITY_THRESHOLD, False)]
    # A cut or a fade from black is a deliberate jump, which frames.py passes whatever it measures.
    continuing = [b for b in record.get("boundaries", []) if b.get("opening_state") == "continue"]
    worst = max((b.get("mad", 0.0) for b in continuing), default=None)
    threshold = record.get("threshold", common.CONTINUITY_THRESHOLD)
    return [GateResult("continuity", worst, threshold, all(b.get("pass") is True for b in continuing))]


def _first_stream(probe: dict | None, kind: str) -> dict:
    """The probe's first stream of ``kind``, such as "audio", or {} when it has none."""
    return next((stream for stream in (probe or {}).get("streams", []) if stream.get("codec_type") == kind), {})


def _audio_s(probe: dict | None) -> float | None:
    return _seconds(_first_stream(probe, "audio").get("duration"))


def _manimlib_beside(mp4: Path) -> GateResult:
    # manimlib is ManimGL's package: code beside the video that names it, even in a comment,
    # was not written for ManimCE, and a video made without the skill has no lesson.py to parse.
    count = sum(
        "manimlib" in py.read_text(encoding="utf-8", errors="replace")
        for py in mp4.parent.glob("*.py") if py.is_file()
    )
    return GateResult("no manimlib beside", count, None, count == 0)


def _frame_rate(stream: dict) -> float | None:
    """The stream's average frame rate, which ffprobe gives as a fraction such as 15/1."""
    try:
        rate = float(Fraction(str(stream.get("avg_frame_rate"))))
    except (ValueError, ZeroDivisionError):
        return None
    return rate if rate > 0 else None


def _sample_times(duration_s: float, fps: float | None) -> list[float]:
    """Every SAMPLE_EVERY_S seconds after the start, or a third and two thirds of the way through a
    video too short for two of those.

    The first frame is never sampled: a lesson that opens from black renders it black. A sample
    past the last frame's start would read nothing, so samples are clamped as frames.py's stills are.
    """
    times = [float(t_s) for t_s in range(SAMPLE_EVERY_S, math.ceil(duration_s), SAMPLE_EVERY_S)]
    if len(times) < 2:
        times = [duration_s / 3, 2 * duration_s / 3]
    return times if fps is None else [frames.clamp_time(t_s, duration_s, fps) for t_s in times]


def _samples(mp4: Path, probe: dict | None) -> list[bytes]:
    """The sampled frames in frames.py's 64x36 grayscale; RuntimeError, naming the reason, when one
    cannot be read.

    Samples follow the video stream, which can end before the audio does.
    """
    video = _first_stream(probe, "video")
    duration_s = _seconds(video.get("duration"))
    if duration_s is None or duration_s <= 0:
        raise RuntimeError("no video stream duration")
    return [frames.gray_small(mp4, t_s) for t_s in _sample_times(duration_s, _frame_rate(video))]


def _frame_rows(mp4: Path, probe: dict | None) -> list[GateResult]:
    """not black and not frozen over the sampled frames; an unreadable frame fails both, with the reason.

    not black judges the median sample's lit share and not frozen the largest change between
    consecutive samples: a lesson's black opening, a fade through black at a scene boundary and a
    long hold are deliberate, while a video that is black for most of its length or never changes is
    broken.
    """
    try:
        samples = _samples(mp4, probe)
    except RuntimeError as exc:
        unreadable = f"{UNREADABLE}: {exc}"
        return [
            GateResult("not black", unreadable, BLACK_LIT_SHARE, False),
            GateResult("not frozen", unreadable, IDENTICAL_MAD, False),
        ]
    lit = statistics.median(sum(pixel > LIT_LUMA for pixel in frame) / len(frame) for frame in samples)
    change = max(frames.mad(a, b) for a, b in zip(samples, samples[1:]))
    return [
        GateResult("not black", round(lit, 4), BLACK_LIT_SHARE, lit >= BLACK_LIT_SHARE),
        GateResult("not frozen", round(change, 6), IDENTICAL_MAD, change >= IDENTICAL_MAD),
    ]


def external(mp4: Path) -> list[GateResult]:
    """The gates that need no lesson, one row each; a missing or unreadable MP4 fails them, not the run."""
    present = mp4.is_file()
    probe = _probe(mp4) if present else None
    container_s = _seconds(_dig(probe, "format", "duration"))
    return [
        GateResult("exists", "present" if present else MISSING, None, present),
        _stream_row(probe),
        _within("container vs audio", container_s, _audio_s(probe), common.SYNC_CONTAINER_TOLERANCE_S),
        _manimlib_beside(mp4),
        *_frame_rows(mp4, probe),
    ]


# In the order of the spec's hard-gate table.
GATES: tuple[Callable[[dict, Path, str], list[GateResult]], ...] = (
    streams,
    container_duration,
    run_log_vs_section_index,
    wav_within_beat,
    marks_inside_beat,
    overrun,
    banned_names,
    index_coverage,
    latex_error,
    continuity,
)


def _cells(g: GateResult) -> tuple[str, str, str]:
    """A gate's measured value, tolerance and result as report.md and --external print them."""
    measured = f"{g.measured:.3f}" if isinstance(g.measured, float) else "n/a" if g.measured is None else str(g.measured)
    tolerance = "none" if g.tolerance is None else f"{g.tolerance:g}"
    return measured, tolerance, "pass" if g.passed else "fail"


def _gate_table(gates: list[GateResult]) -> str:
    rows = ["| Gate | Measured | Tolerance | Result |", "| --- | --- | --- | --- |"]
    for g in gates:
        measured, tolerance, result = _cells(g)
        rows.append(f"| {g.gate} | {measured} | {tolerance} | {result} |")
    return "\n".join(rows)


def _output_line(lesson: dict, run_dir: Path, tier: str) -> str:
    mp4 = output_path(lesson, run_dir, tier)
    # The run directory as the repository root sees it: mtv-runs/<slug> in the spec's layout.
    shown_path = Path(*run_dir.resolve().parts[-2:]) / mp4.relative_to(run_dir)
    duration_s = _container_s(mp4)
    width, height, fps = common.TIERS[tier]
    duration = "n/a" if duration_s is None else f"{duration_s:.2f}"
    return f"Output: {shown_path.as_posix()} ({duration} s, {tier}, {width}x{height}@{fps})"


def _narration_line(lesson: dict) -> str:
    # The stage's tools name the provider that ran, which --provider may have overridden.
    tools = _dig(lesson, "stages", "narrate", "tools") or {}
    provider = tools.get("provider") or lesson.get("provider") or "n/a"
    model = tools.get("model") or ("offline weights" if provider == "kokoro" else "n/a")
    return f"Narration: {provider}, voice {lesson.get('voice') or 'n/a'}, model {model}"


def _font(lesson: dict) -> str:
    font = _dig(lesson, "env", "font")
    # look.pick_font returns an empty name when no candidate is installed and Pango picks.
    return "n/a" if font is None else font or "Pango default serif"


def _exemplars(lesson: dict) -> str:
    exemplars = lesson.get("exemplars") or {}
    # Without the sha256 of a checked index the run went on without exemplars.
    if not (exemplars.get("dir") and exemplars.get("index_sha256")):
        return "none"
    commit = _dig(_read_json(Path(exemplars["dir"]) / "index.json"), "corpus_commit") or "unknown"
    used = exemplars.get("used") or {}
    parts = [f"corpus {commit}", f"storyboarder {', '.join(used.get('storyboarder') or []) or 'none'}"]
    for scene, ids in (used.get("frame-critic") or {}).items():
        parts.append(f"frame-critic {scene} {', '.join(ids) or 'none'}")
    return "; ".join(parts)


def _score(entry: Any) -> str:
    """A rubric total out of RUBRIC_MAX, or a check's bare verdict when it carries no scores."""
    scores = _dig(entry, "scores")
    if isinstance(scores, dict):
        return f"{sum(_number(value) or 0 for value in scores.values()):g}/{RUBRIC_MAX}"
    passed = _dig(entry, "pass")
    return "n/a" if passed is None else "pass" if passed else "fail"


def _rubric(lesson: dict) -> str:
    checks = lesson.get("checks") or {}
    per_scene = _dig(checks, "frames", "scenes") or {}
    scenes = ", ".join(f"{scene}: {_score(entry)}" for scene, entry in per_scene.items()) or "n/a"
    final = _dig(checks, "frames", "final")
    final_text = "n/a"
    if isinstance(final, dict):
        zeros = ", ".join(final.get("zeros") or []) or "none"
        final_text = f"{_score(final)} (minimum per item across scenes), zeros: {zeros}"
    return f"storyboard {_score(checks.get('storyboard'))}; frames per scene {scenes}; final {final_text}"


def _warnings(lesson: dict) -> list[str]:
    beats = [beat for _, beat in mtv_lesson.beats(lesson)]
    warnings = []
    interpolated = [beat["id"] for beat in beats if beat.get("interpolated")]
    if interpolated:
        warnings.append(f"interpolated beats: {', '.join(interpolated)}")
    exemplars = lesson.get("exemplars") or {}
    if exemplars.get("dir") and exemplars.get("index_sha256") is None:
        warning = f"exemplar check failed for {exemplars['dir']}; continuing without exemplars"
        # The parent files exemplars.py check's findings here once it records them (M3).
        if exemplars.get("check_findings"):
            warning += ": " + "; ".join(exemplars["check_findings"])
        warnings.append(warning)
    fallback = _dig(lesson, "stages", "narrate", "tools", "fallback")
    if fallback:
        warnings.append(f"provider fallback to {fallback}")
    for beat in beats:
        overrun_s = _number(_dig(beat, "render", "log", "overrun_s"))
        # The mixin measures an overrun on CE's clock, a running sum of 1/fps steps, so a beat that
        # ends on its target can log float noise (5e-15 s): only what shows in milliseconds counts.
        if overrun_s is not None and round(overrun_s, 3) > 0:
            warnings.append(f"overrun {beat['id']}: {overrun_s:.3f} s")
    return warnings


def write_report(lesson: dict, run_dir: Path, tier: str, gates: list[GateResult]) -> None:
    """report.md in the spec's template, one field per paragraph so that it renders as it reads."""
    warnings = _warnings(lesson)

    def wall(stage: str) -> str:
        value = _dig(lesson, "stages", stage, "tools", "wall_clock_s")
        return "n/a" if value is None else f"{value} s"

    jobs = _dig(lesson, "stages", f"render.{tier}", "tools", "jobs") or "n/a"
    up_to_date = [stage for stage in mtv_lesson.STAGES if not mtv_lesson.needs_rerun(lesson, stage)]
    passed = sum(g.passed for g in gates)
    paragraphs = [
        f"# {lesson.get('title') or lesson['slug']}",
        _output_line(lesson, run_dir, tier),
        _narration_line(lesson),
        f"Font: {_font(lesson)}",
        f"Exemplars: {_exemplars(lesson)}",
        f"Rubric: {_rubric(lesson)}",
        f"Hard gates: {passed} of {len(gates)} pass\n\n{_gate_table(gates)}",
        "Warnings:" + ("\n\n" + "\n".join(f"- {warning}" for warning in warnings) if warnings else " none"),
        f"Attempts: `{json.dumps(lesson.get('attempts') or {}, sort_keys=True)}`",
        f"Render: draft {wall('render.draft')} wall clock, standard {wall('render.standard')} wall clock, jobs {jobs}",
        "Resume: rerun the skill in this directory; "
        + (f"stages {', '.join(up_to_date)} are up to date" if up_to_date else "no stage is up to date"),
    ]
    (run_dir / "report.md").write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8")


def _verdict(label: str, gates: list[GateResult]) -> int:
    failing = [g.gate for g in gates if not g.passed]
    return common.verdict(not failing, f"{label}: " + (", ".join(failing) if failing else f"{len(gates)} gates"))


def run_external(mp4: Path) -> int:
    gates = external(mp4)
    for g in gates:
        measured, tolerance, result = _cells(g)
        print(f"{g.gate}: {measured} (tolerance {tolerance}) {result}")
    return _verdict("verify --external", gates)


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Run the hard gates on the assembled lesson and write report.md.", positional=False)
    parser.add_argument("lesson", type=Path, nargs="?", help="path to lesson.json; omitted with --external")
    parser.add_argument("--tier", choices=tuple(common.TIERS), help="the tier assembled")
    parser.add_argument("--external", type=Path, metavar="MP4", help="check an MP4 made without a lesson")
    args = parser.parse_args(argv)
    if args.external is not None:
        if args.lesson is not None or args.tier is not None:
            return common.usage_error("--external takes the MP4 alone, without lesson.json or --tier")
        absent = [tool for tool in ("ffmpeg", "ffprobe") if common.which(tool) is None]
        if absent:
            return common.usage_error(" and ".join(absent) + " not on PATH")
        return run_external(args.external)
    if args.lesson is None or args.tier is None:
        return common.usage_error("lesson.json and --tier are required unless --external is given")
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    if common.which("ffprobe") is None:
        return common.usage_error("ffprobe is not on PATH")
    if not (isinstance(lesson.get("slug"), str) and lesson["slug"]):
        return common.usage_error("lesson has no slug to find the assembled video by")
    run_dir = args.lesson.parent
    mp4 = output_path(lesson, run_dir, args.tier)
    if not mp4.is_file():
        return common.usage_error(f"run assemble.py --tier {args.tier} first: {mp4} is missing")
    gates = [result for gate in GATES for result in gate(lesson, run_dir, args.tier)]
    ok = all(g.passed for g in gates)
    rows = [g.as_dict() for g in gates]
    lesson.setdefault("checks", {})["verify"] = {"pass": ok, "at": common.now_iso(), "gates": rows}
    # The stage is the verify of the tier the lesson is delivered at: its hash holds lesson.tier
    # but not --tier, and none of the outputs the gates read. So a failure, or a run at another
    # tier, drops the stage, and a resumed run never takes an earlier pass for this verdict.
    # Marked before the report is written, so that its resume line counts this stage.
    if ok and args.tier == lesson.get("tier"):
        mtv_lesson.mark_done(lesson, "verify", {"tier": args.tier})
    else:
        (lesson.get("stages") or {}).pop("verify", None)
    write_report(lesson, run_dir, args.tier, gates)
    mtv_lesson.save(lesson, args.lesson)
    return _verdict("verify", gates)


if __name__ == "__main__":
    sys.exit(main())
