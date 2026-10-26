"""Join the rendered beats and their narration into the lesson's MP4 and its subtitles.

Every beat's WAV is trimmed or padded to its rendered duration before the WAVs are joined,
so each narration starts where its beat starts in the joined video.
"""

from __future__ import annotations

import json
import math
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mtv import common
from mtv import lesson as mtv_lesson

NARRATION_RATE = 24000
LOUDNORM_TARGET = "I=-16:TP=-1.5:LRA=11"
# 3b1b's renders take eq=saturation=1.5 at encode (ManimGL's scene_file_writer, set by 3b1b's
# custom_config.yml), and ManimCE has no such option, so the look is applied here.
DEFAULT_SATURATION = 1.5
# loudnorm's first-pass report keys, each mapped to the second-pass option that takes it.
_MEASURED = {
    "input_i": "measured_I",
    "input_lra": "measured_LRA",
    "input_tp": "measured_TP",
    "input_thresh": "measured_thresh",
    "target_offset": "offset",
}


def _ffmpeg(*args: str) -> str:
    """Run ffmpeg and return its stderr, which carries loudnorm's report."""
    # Without -nostdin ffmpeg reads its interactive keys from the inherited stdin, which
    # swallows piped input and stops a background job.
    completed = common.run_cmd(["ffmpeg", "-nostdin", *args])
    completed.check_returncode()
    return completed.stderr


def concat_list(paths: list[Path], out_txt: Path) -> None:
    # The concat demuxer resolves a relative path against the list file's directory, and
    # reads each path between single quotes, inside which a quote is written '\''.
    lines = ["file '" + str(path.resolve()).replace("'", "'\\''") + "'" for path in paths]
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _concat(list_txt: Path, out: Path) -> None:
    # -safe 0 admits the absolute paths concat_list writes.
    _ffmpeg("-y", "-f", "concat", "-safe", "0", "-i", str(list_txt), "-c", "copy", str(out))


def pad_beat_audio(wav: Path, duration_s: float, out_wav: Path) -> None:
    d = f"{duration_s:.6f}"
    _ffmpeg(
        "-y", "-i", str(wav), "-af", f"atrim=0:{d},apad=whole_dur={d}",
        "-ar", str(NARRATION_RATE), "-ac", "1", str(out_wav),
    )


def loudnorm_two_pass(in_wav: Path, out_wav: Path) -> dict:
    """Normalize ``in_wav`` to ``LOUDNORM_TARGET`` into ``out_wav``; return the first pass's measurement."""
    stderr = _ffmpeg("-i", str(in_wav), "-af", f"loudnorm={LOUDNORM_TARGET}:print_format=json", "-f", "null", "-")
    report = json.loads(stderr[stderr.rindex("{") : stderr.rindex("}") + 1])
    measured = {option: report[key] for key, option in _MEASURED.items()}
    if not math.isfinite(float(report["input_i"])):
        # Silence (the null provider's narration) measures -inf, which the second pass
        # rejects as out of range, and has no loudness to correct.
        shutil.copyfile(in_wav, out_wav)
        return measured
    options = ":".join(f"{option}={value}" for option, value in measured.items())
    # loudnorm upsamples to 192 kHz, linear mode included (measured with ffmpeg 6.1.1), so its
    # output is resampled back to the narration rate.
    _ffmpeg(
        "-y", "-i", str(in_wav), "-af", f"loudnorm={LOUDNORM_TARGET}:{options}:linear=true:dual_mono=true",
        "-ar", str(NARRATION_RATE), str(out_wav),
    )
    return measured


def mux(video: Path, audio: Path, out_mp4: Path, saturation: float) -> None:
    if saturation != 1.0:
        video_args = [
            "-vf", f"eq=saturation={saturation}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p",
        ]
    else:
        video_args = ["-c:v", "copy"]
    # The maps keep the output to the one video and one narration stream verify.py gates on,
    # whatever streams the inputs carry.
    _ffmpeg(
        "-y", "-i", str(video), "-i", str(audio), "-map", "0:v:0", "-map", "1:a:0", *video_args,
        "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_mp4),
    )


def srt_timestamp(t_s: float) -> str:
    ms = round(t_s * 1000)
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def write_srt(cues: list[tuple[float, float, str]], path: Path) -> None:
    # A blank line ends a cue, so each text is written on one line.
    blocks = [
        f"{n}\n{srt_timestamp(start_s)} --> {srt_timestamp(end_s)}\n{' '.join(text.split())}\n"
        for n, (start_s, end_s, text) in enumerate(cues, 1)
    ]
    path.write_text("\n".join(blocks), encoding="utf-8")


def _unnarrated(lesson: dict, run_dir: Path) -> list[str]:
    """Each beat without a narration WAV on disk and the duration narrate.py measured for it."""
    return [
        f"{beat['id']}: no audio"
        for _, beat in mtv_lesson.beats(lesson)
        if not (
            isinstance(beat.get("audio"), str)
            and (run_dir / beat["audio"]).is_file()
            and isinstance(beat.get("duration_s"), (int, float))
        )
    ]


def _join(beats: list[dict], run_dir: Path, tier: str, final: Path, saturation: float) -> None:
    """Mux the joined beat videos and the joined, normalized narration into ``final``, keeping
    the joined silent video and narration track beside it."""
    silent = final.parent / f".silent.{tier}.mp4"
    narration = final.parent / f".narration.{tier}.wav"
    with tempfile.TemporaryDirectory(prefix="mtv-assemble-") as tmp:
        work = Path(tmp)
        concat_list([run_dir / beat["render"]["video"] for beat in beats], work / "video.txt")
        _concat(work / "video.txt", silent)
        padded = [work / f"{beat['id']}.wav" for beat in beats]
        for beat, padded_wav in zip(beats, padded):
            pad_beat_audio(run_dir / beat["audio"], beat["render"]["duration_s"], padded_wav)
        concat_list(padded, work / "audio.txt")
        _concat(work / "audio.txt", narration)
        loudnorm_two_pass(narration, work / "narration.wav")
        mux(silent, work / "narration.wav", final, saturation)


def _cues(beats: list[dict]) -> list[tuple[float, float, str]]:
    """One cue per beat, for as long as its narration, from where the joined video starts the beat."""
    cues = []
    start_s = 0.0
    for beat in beats:
        cues.append((start_s, start_s + beat["duration_s"], beat["narration"]))
        start_s += beat["render"]["duration_s"]
    return cues


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Join the rendered beats and their narration into the lesson's MP4 and SRT.")
    parser.add_argument("--tier", choices=tuple(common.TIERS), required=True, help="the render tier to assemble")
    parser.add_argument(
        "--saturation", type=float, default=DEFAULT_SATURATION,
        help=f"eq saturation of the encode (default {DEFAULT_SATURATION}); 1.0 copies the video without re-encoding",
    )
    args = parser.parse_args(argv)
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    missing_tools = [tool for tool in ("ffmpeg", "ffprobe") if common.which(tool) is None]
    if missing_tools:
        return common.usage_error(" and ".join(missing_tools) + " not on PATH")
    slug = lesson.get("slug")
    if not (isinstance(slug, str) and slug):
        return common.usage_error("lesson has no slug to name the outputs after")
    run_dir = args.lesson.parent
    problems = _unnarrated(lesson, run_dir) + mtv_lesson.unrendered(lesson, run_dir, args.tier)
    if problems:
        return common.usage_error(f"run narrate.py and render.py --tier {args.tier} first: " + "; ".join(problems))
    beats = [beat for _, beat in mtv_lesson.beats(lesson)]
    final = run_dir / "out" / f"{slug}.{args.tier}.mp4"
    srt = final.with_name(f"{slug}.srt")
    final.parent.mkdir(exist_ok=True)
    # A failed run leaves neither an earlier run's video and SRT nor a partial file, which
    # verify.py would check in place of this run's.
    final.unlink(missing_ok=True)
    srt.unlink(missing_ok=True)
    try:
        _join(beats, run_dir, args.tier, final, args.saturation)
        duration_s = float(common.ffprobe_json(final)["format"]["duration"])
    # A beat file ffmpeg cannot read is bad input to this stage, not a failed gate.
    except subprocess.CalledProcessError as exc:
        final.unlink(missing_ok=True)
        lines = (exc.stderr or "").strip().splitlines()
        reason = lines[-1] if lines else f"exit status {exc.returncode}"
        return common.usage_error(f"{shlex.join(exc.cmd)} failed: {reason}")
    write_srt(_cues(beats), srt)
    mtv_lesson.mark_done(lesson, "assemble", {"saturation": str(args.saturation)})
    mtv_lesson.save(lesson, args.lesson)
    return common.verdict(True, f"assembled out/{final.name} ({duration_s:.2f} s)")


if __name__ == "__main__":
    sys.exit(main())
