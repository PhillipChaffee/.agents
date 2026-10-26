"""Render every scene of the generated lesson.py in its own manim process, then read its beats back.

One process per scene lets scenes render side by side, and lets one scene fail, hang or be
retried while the others finish. The mixin opens a section per beat, so CE's section index
holds one MP4 per beat; this script copies that index and its MP4s into the scene's render
directory and fills each beat's render block of lesson.json from it and from the mixin's
run log.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mtv import common
from mtv import lesson as mtv_lesson

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = Path(__file__).resolve().parent.parent
POLL_S = 0.5
TAIL_LINES = 20


def _config_file(tier: str) -> Path:
    return SKILL_DIR / "assets" / f"manim.cfg.{tier}"


def _scenes_file(lesson_path: Path) -> Path:
    # No CLI names the generated scenes file, so it is the one the run directory layout puts
    # beside lesson.json.
    return lesson_path.resolve().parent / "lesson.py"


def scene_command(lesson_py: Path, scene_class: str, cfg: Path, media_dir: Path, disable_caching: bool) -> list[str]:
    # CE options: --config_file and --disable_caching (manim/cli/render/global_options.py:60-70),
    # --save_sections (render_options.py:260), --media_dir (output_options.py:24). Every option
    # precedes the file and the class, so the class is always the last argument.
    argv = ["manim", "render", "--config_file", str(cfg), "--save_sections", "--media_dir", str(media_dir)]
    if disable_caching:
        argv.append("--disable_caching")
    return [*argv, str(lesson_py), scene_class]


def _pythonpath(scripts_dir: Path) -> str:
    # First, so that a scene's "from mtv..." imports this skill's package whatever else is set.
    inherited = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    return os.pathsep.join([str(scripts_dir), *(part for part in inherited if part and part != str(scripts_dir))])


def scene_env(scripts_dir: Path, run_log: Path, lesson_path: Path) -> dict[str, str]:
    """manim's environment: the scene imports mtv from ``scripts_dir``, the mixin appends one
    line per beat to MTV_RUN_LOG, and load_lesson reads the lesson named by MTV_LESSON."""
    return {
        **os.environ,
        "PYTHONPATH": _pythonpath(scripts_dir),
        "MTV_RUN_LOG": str(run_log),
        "MTV_LESSON": str(lesson_path.resolve()),
    }


def _size(path: Path) -> int:
    try:
        return path.stat().st_size
    except FileNotFoundError:
        return 0


def run_with_watchdog(
    argv: list[str], env: dict[str, str], cwd: Path, render_log: Path, run_log: Path, hang_timeout_s: float
) -> tuple[int | None, float]:
    """Run ``argv`` with its output appended to ``render_log``; return its exit status, or None
    when it was killed because neither log grew for ``hang_timeout_s``, and its wall time.

    Growth counts bytes, not lines, because CE redraws its progress bar with a carriage return
    and no newline, so a long animation is busy for minutes without a new line. stdin is closed
    because CE asks on stdin which scene to render when the requested class is missing from a
    file with several (manim/utils/module_ops.py:109-142); without stdin it fails at once
    instead of waiting for the detector.
    """
    start = time.monotonic()
    with open(render_log, "ab") as log:
        process = subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env=env, cwd=cwd
        )
    sizes, grew_at = (_size(render_log), _size(run_log)), start
    while True:
        try:
            return process.wait(timeout=POLL_S), time.monotonic() - start
        except subprocess.TimeoutExpired:
            pass
        now, current = time.monotonic(), (_size(render_log), _size(run_log))
        if current != sizes:
            sizes, grew_at = current, now
        elif now - grew_at >= hang_timeout_s:
            process.kill()
            process.wait()
            return None, now - start


def _section_indexes(out_dir: Path, scene_class: str) -> list[Path]:
    # CE writes {media_dir}/videos/{module_name}/{quality}/sections/<Scene>.json
    # (manim/_config/default.cfg:75-76, manim/_config/output_plan.py:345-347).
    return sorted((out_dir / "media" / "videos").glob(f"*/*/sections/{scene_class}.json"))


def collect_sections(out_dir: Path, scene_class: str) -> list[dict]:
    """CE's section index for ``scene_class``, copied with its MP4s into ``out_dir``; empty when CE wrote none.

    Each entry holds name, type, video (a path relative to the index), width, height,
    nb_frames, duration, avg_frame_rate, codec_name and pix_fmt (manim/scene/section.py:83-104,
    manim/utils/commands.py:47-67), so the copy beside the MP4s stays a valid index.
    """
    indexes = _section_indexes(out_dir, scene_class)
    if not indexes:
        return []
    entries = common.load_json(indexes[0])
    shutil.copyfile(indexes[0], out_dir / "sections.json")
    for entry in entries:
        shutil.copyfile(indexes[0].parent / entry["video"], out_dir / entry["video"])
    return entries


def _log_text(render_log: Path) -> str:
    # A non-UTF-8 byte from a tool manim ran must not cost the error text around it.
    return render_log.read_text(encoding="utf-8", errors="replace")


def _matched_row(render_log: Path) -> common.ErrorRow | None:
    # The whole log, not its tail: with several classes in the file, CE's ERROR record for a
    # missing class sits above the scene list and the prompt that follow it.
    return common.match_error(_log_text(render_log))


def _append(render_log: Path, lines: list[str]) -> None:
    with open(render_log, "a", encoding="utf-8") as log:
        log.writelines(f"{line}\n" for line in lines)


def _failure(render_log: Path, error: common.ErrorRow | None) -> dict:
    return {"ok": False, "error": error, "tail": _log_text(render_log).splitlines()[-TAIL_LINES:]}


def _missing(beat_ids: list[str], found: dict, where: str) -> list[str]:
    return [f"mtv: beat {beat_id} missing from {where}" for beat_id in beat_ids if beat_id not in found]


def _run_log_lines(run_log: Path) -> dict[str, dict]:
    records = (json.loads(line) for line in run_log.read_text(encoding="utf-8").splitlines() if line.strip())
    return {record["beat"]: record for record in records}


def render_scene(lesson: dict, lesson_path: Path, scene: dict, tier: str, hang_timeout_s: float) -> dict:
    """Render ``scene``, once more with caching off after a hang, and fill its beats' render blocks.

    Returns ``{"ok": True, "wall_s": s}``, or ``{"ok": False, "error": the matched ERROR_TABLE
    row or None, "tail": the last lines of render.log}``. Scenes render on parallel threads,
    and each writes only its own scene's beats and its own render_retries key.
    """
    run_dir = lesson_path.resolve().parent
    out_dir = run_dir / "render" / tier / scene["id"]
    media_dir = out_dir / "media"
    render_log, run_log = out_dir / "render.log", out_dir / "run.log"
    lesson_py, env = _scenes_file(lesson_path), scene_env(SCRIPTS_DIR, run_log, lesson_path)

    def attempt(disable_caching: bool) -> tuple[int | None, float]:
        # A retried scene must not keep the hung attempt's beat lines.
        run_log.write_bytes(b"")
        argv = scene_command(lesson_py, scene["scene_class"], _config_file(tier), media_dir, disable_caching)
        returncode, wall_s = run_with_watchdog(argv, env, run_dir, render_log, run_log, hang_timeout_s)
        if returncode is None:
            _append(render_log, [f"mtv: no new output in render.log or run.log for {hang_timeout_s:g} s; killed"])
        return returncode, wall_s

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        # verify.py's latex gate reads the whole render.log, so an error an earlier run fixed must go.
        render_log.write_bytes(b"")
        # CE exits 0 having rendered another class when the requested one is missing from a file
        # with one other scene (manim/utils/module_ops.py:103-108), so an index left by an earlier
        # render would pass for this one.
        for stale in _section_indexes(out_dir, scene["scene_class"]):
            stale.unlink()
        returncode, wall_s = attempt(False)
        if returncode is None:
            mtv_lesson.bump(lesson, "render_retries", scene["id"])
            returncode, retry_s = attempt(True)
            wall_s += retry_s
        if returncode != 0:
            return _failure(render_log, _matched_row(render_log))
        entries = collect_sections(out_dir, scene["scene_class"])
        positions = {entry["name"]: index for index, entry in enumerate(entries)}
        records = _run_log_lines(run_log)
        beats = scene.get("beats", [])
        # A beat without a section lacks its run-log line for the same reason, so the run log is
        # checked only once every beat has its section.
        beat_ids = [beat["id"] for beat in beats]
        missing = _missing(beat_ids, positions, "the section index") or _missing(beat_ids, records, "run.log")
        if missing:
            # Matched first, because CE's ERROR record for the missing class (row 19) names the
            # cause, while the missing-beat line appended below (row 16) names only the symptom.
            cause = _matched_row(render_log)
            _append(render_log, missing)
            return _failure(render_log, cause or _matched_row(render_log))
        for beat in beats:
            entry = entries[positions[beat["id"]]]
            beat.setdefault("render", {}).update(
                index=positions[beat["id"]],
                video=(out_dir.relative_to(run_dir) / entry["video"]).as_posix(),
                duration_s=float(entry["duration"]),
                log={key: value for key, value in records[beat["id"]].items() if key != "beat"},
            )
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return {"ok": False, "error": None, "tail": [f"mtv: {exc}"]}
    return {"ok": True, "wall_s": wall_s}


def _first_line(argv: list[str], env: dict[str, str] | None = None) -> str | None:
    """The first line ``argv`` prints, or None when it is absent, fails or prints nothing."""
    try:
        completed = common.run_cmd(argv, env=env)
    except OSError:
        return None
    lines = completed.stdout.splitlines()
    return lines[0].strip() if completed.returncode == 0 and lines else None


def record_env(lesson: dict, scripts_dir: Path) -> None:
    pythonpath = _pythonpath(scripts_dir)
    # The font comes from the interpreter and path the scenes run with, since look.py imports manim.
    font_probe = [sys.executable, "-c", "from mtv.look import pick_font; print(pick_font())"]
    lesson.setdefault("env", {}).update(
        pythonpath=pythonpath,
        manim=_first_line(["manim", "--version"]),
        ffmpeg=_first_line(["ffmpeg", "-version"]),
        python=platform.python_version(),
        font=_first_line(font_probe, env={**os.environ, "PYTHONPATH": pythonpath}),
    )


def _rendered(scene: dict, tier: str, run_dir: Path) -> bool:
    """Whether every beat of ``scene`` has a video from a render at ``tier`` that is still on disk."""
    prefix = f"render/{tier}/{scene['id']}/"
    videos = [beat.get("render", {}).get("video") for beat in scene.get("beats", [])]
    return all(isinstance(video, str) and video.startswith(prefix) and (run_dir / video).exists() for video in videos)


def _failure_text(scene_id: str, result: dict) -> str:
    row = result["error"]
    if row is not None:
        return f"{scene_id}: {row.gl_idiom} | fix: {row.fix_text}"
    last = next((line.strip() for line in reversed(result["tail"]) if line.strip()), "no output")
    return f"{scene_id}: {last} | fix: see render.log"


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Render each scene of lesson.py in its own manim process.")
    parser.add_argument("--tier", required=True, choices=sorted(common.TIERS), help="render tier")
    parser.add_argument(
        "--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1), help="scenes rendered at once; default CPUs - 1"
    )
    parser.add_argument("--scenes", help="comma-separated scene ids to render; default every scene")
    parser.add_argument(
        "--hang-timeout-s",
        type=float,
        default=common.HANG_TIMEOUT_S,
        help="kill a render whose render.log and run.log stay unchanged this long",
    )
    args = parser.parse_args(argv)
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    if args.jobs < 1:
        return common.usage_error("--jobs must be at least 1")
    if args.scenes is None:
        scenes = lesson.get("scenes", [])
    else:
        try:
            scenes = [mtv_lesson.scene_by_id(lesson, scene_id) for scene_id in dict.fromkeys(args.scenes.split(","))]
        except KeyError as exc:
            return common.usage_error(f"no scene with id {exc}")
    # validate leaves scene_class optional, since a lesson has none before its storyboard.
    unclassed = [f"{scene['id']}: missing field 'scene_class'" for scene in scenes if "scene_class" not in scene]
    if unclassed:
        return common.usage_error("lesson invalid: " + "; ".join(unclassed))
    if common.which("manim") is None:
        return common.usage_error("manim is not on PATH; activate the venv that has ManimCE")
    if not _config_file(args.tier).exists():
        return common.usage_error(f"config file missing: {_config_file(args.tier)}")
    if not _scenes_file(args.lesson).exists():
        return common.usage_error(f"scenes file missing: {_scenes_file(args.lesson)}")
    start = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        outcomes = pool.map(
            lambda scene: render_scene(lesson, args.lesson, scene, args.tier, args.hang_timeout_s), scenes
        )
        results = dict(zip((scene["id"] for scene in scenes), outcomes))
    total = time.monotonic() - start
    record_env(lesson, SCRIPTS_DIR)
    failed = {scene_id: result for scene_id, result in results.items() if not result["ok"]}
    # The stage is done only when every scene of the lesson has this tier's render, so a run
    # limited by --scenes leaves it open while another scene has none.
    run_dir = args.lesson.resolve().parent
    if not failed and all(_rendered(scene, args.tier, run_dir) for scene in lesson.get("scenes", [])):
        mtv_lesson.mark_done(lesson, f"render.{args.tier}", {"wall_clock_s": f"{total:.1f}", "jobs": str(args.jobs)})
    mtv_lesson.save(lesson, args.lesson)
    for scene_id, result in failed.items():
        print(f"{scene_id}: render failed")
        for line in result["tail"]:
            print(line)
    if failed:
        return common.verdict(False, "; ".join(_failure_text(scene_id, result) for scene_id, result in failed.items()))
    return common.verdict(True, f"rendered {len(results)} scenes in {total:.1f} s")


if __name__ == "__main__":
    sys.exit(main())
