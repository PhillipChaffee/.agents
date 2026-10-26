"""Write the frames a reviewer reads for every rendered beat, and measure each scene boundary.

Each beat gets a still at every mark, its last frame, its first frame when it opens a
scene, and a six-frame contact sheet in the corpus sheets' geometry. continuity.json
compares the frames either side of every scene boundary; verify.py gates on it.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from mtv import common
from mtv import lesson as mtv_lesson

try:
    from PIL import Image, ImageDraw
except ImportError:
    # Only the sheets need Pillow; the continuity measure reads raw pixels from ffmpeg.
    Image = ImageDraw = None

GRAY_SIZE = (64, 36)
TILE_SIZE = (426, 240)
SHEET_GRID = (3, 2)  # columns, rows
# Pillow's default font at its default 10 px is hard to read on a 240-pixel tile.
STAMP_FONT_PX = 16


def extract_frame(video: Path, t_s: float, out_png: Path) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    # ffmpeg exits 0 without writing when the seek passes the last frame, so a stale
    # file must not stand in for the missing one.
    out_png.unlink(missing_ok=True)
    argv = ["ffmpeg", "-y", "-ss", f"{t_s:.6f}", "-i", str(video), "-frames:v", "1", "-update", "1", str(out_png)]
    completed = common.run_cmd(argv)
    if completed.returncode != 0 or not out_png.exists():
        raise RuntimeError(_no_frame(video, t_s, completed.stderr))


def gray_small(video: Path, t_s: float) -> bytes:
    """The frame at ``t_s`` as 64x36 8-bit grayscale, row by row."""
    width, height = GRAY_SIZE
    argv = [
        "ffmpeg", "-ss", f"{t_s:.6f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:{height}",
        "-f", "rawvideo", "-pix_fmt", "gray", "-",
    ]
    # Raw pixels on stdout are bytes, which common.run_cmd would decode as text.
    completed = subprocess.run(argv, capture_output=True, check=False)
    if completed.returncode != 0 or len(completed.stdout) != width * height:
        raise RuntimeError(_no_frame(video, t_s, completed.stderr.decode(errors="replace")))
    return completed.stdout


def _no_frame(video: Path, t_s: float, stderr: str) -> str:
    lines = stderr.strip().splitlines()
    return f"ffmpeg read no frame at {t_s:.3f} s of {video}: {lines[-1] if lines else 'no output'}"


def mad(a: bytes, b: bytes) -> float:
    """Mean absolute difference of two equal-sized 8-bit images, from 0 (equal) to 1."""
    if not a or len(a) != len(b):
        raise ValueError(f"cannot compare images of {len(a)} and {len(b)} bytes")
    return sum(abs(x - y) for x, y in zip(a, b)) / (255 * len(a))


def clamp_time(t_s: float, duration_s: float, fps: int) -> float:
    # The last frame starts one frame before the end; a mark at or past the end (frame
    # quantization or an overrun) still gets a still instead of an empty seek.
    return min(max(t_s, 0.0), duration_s - 1 / fps)


def _stamp(t_s: float) -> str:
    # Rounded to tenths first, so 59.97 s reads 01:00.0, never 00:60.0.
    minutes, tenths = divmod(round(t_s * 10), 600)
    return f"{minutes:02d}:{tenths // 10:02d}.{tenths % 10}"


def sheet(video: Path, duration_s: float, t0_label_s: float, out_jpg: Path, fps: int | None = None) -> bool:
    """Six frames evenly spaced over ``video`` as a 1278x480 sheet; False, writing nothing, without Pillow.

    Each tile is stamped with ``t0_label_s`` plus its frame time. Given ``fps``, frame times
    are clamped to the last frame, which the sixth tile passes in a beat under twelve frames.
    """
    if Image is None:
        return False
    columns, rows = SHEET_GRID
    tile_w, tile_h = TILE_SIZE
    canvas = Image.new("RGB", (columns * tile_w, rows * tile_h))
    draw = ImageDraw.Draw(canvas)
    with tempfile.TemporaryDirectory(prefix="mtv-sheet-") as tmp:
        for k in range(columns * rows):
            t_s = duration_s * (k + 0.5) / (columns * rows)
            png = Path(tmp) / f"{k}.png"
            extract_frame(video, t_s if fps is None else clamp_time(t_s, duration_s, fps), png)
            x, y = (k % columns) * tile_w, (k // columns) * tile_h
            with Image.open(png) as frame:
                canvas.paste(frame.convert("RGB").resize(TILE_SIZE), (x, y))
            label = _stamp(t0_label_s + t_s)
            # A black box keeps the white stamp legible over a white frame.
            draw.rectangle(draw.textbbox((x + 4, y + 4), label, font_size=STAMP_FONT_PX), fill="black")
            draw.text((x + 4, y + 4), label, fill="white", font_size=STAMP_FONT_PX)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_jpg, "JPEG", quality=90)
    return True


def beat_frames(run_dir: Path, scene: dict, beat: dict, first: bool, fps: int, scene_t0_s: float) -> list[str]:
    """Write ``beat``'s mark, last, first and sheet frames; return their paths relative to ``run_dir``.

    ``scene_t0_s`` is where the scene starts in the assembled video, so the sheet's stamps
    read as times in the finished lesson.
    """
    video, duration_s = run_dir / beat["render"]["video"], beat["render"]["duration_s"]
    stem = f"frames/{scene['id']}/{beat['id']}"
    shots = [(f"{stem}-{mark}.png", clamp_time(t_s, duration_s, fps)) for mark, t_s in (beat.get("marks_s") or {}).items()]
    shots.append((f"{stem}-last.png", clamp_time(duration_s, duration_s, fps)))
    if first:
        shots.append((f"{stem}-first.png", 0.0))
    for rel, t_s in shots:
        extract_frame(video, t_s, run_dir / rel)
    written = [rel for rel, _ in shots]
    # The assembled video plays the scene's beats back to back.
    beat_t0_s = scene_t0_s
    for earlier in scene["beats"]:
        if earlier is beat:
            break
        beat_t0_s += earlier["render"]["duration_s"]
    if sheet(video, duration_s, beat_t0_s, run_dir / f"{stem}-sheet.jpg", fps):
        written.append(f"{stem}-sheet.jpg")
    return written


def continuity(lesson: dict, run_dir: Path, tier: str) -> dict:
    """The continuity.json record: each scene's last frame against the next scene's first."""
    fps = common.TIERS[tier][2]
    boundaries = []
    for prev, nxt in zip(lesson["scenes"], lesson["scenes"][1:]):
        last_beat, first_beat = prev["beats"][-1], nxt["beats"][0]
        last_s = clamp_time(last_beat["render"]["duration_s"], last_beat["render"]["duration_s"], fps)
        value = mad(
            gray_small(run_dir / last_beat["render"]["video"], last_s),
            gray_small(run_dir / first_beat["render"]["video"], 0.0),
        )
        boundaries.append({
            "from_scene": prev["id"],
            "to_scene": nxt["id"],
            "opening_state": nxt.get("opening_state"),
            "last_frame": f"frames/{prev['id']}/{last_beat['id']}-last.png",
            "first_frame": f"frames/{nxt['id']}/{first_beat['id']}-first.png",
            "mad": value,
            # A cut or a fade from black is a deliberate jump, so only a continuing scene is held to the bound.
            "pass": not (nxt.get("opening_state") == "continue" and value > common.CONTINUITY_THRESHOLD),
        })
    return {
        "schema": common.CONTINUITY_SCHEMA,
        "tier": tier,
        "threshold": common.CONTINUITY_THRESHOLD,
        "boundaries": boundaries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Write every beat's review frames and sheet, and measure the scene boundaries.")
    parser.add_argument("--tier", choices=tuple(common.TIERS), required=True, help="the render tier to review")
    args = parser.parse_args(argv)
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    if common.which("ffmpeg") is None:
        return common.usage_error("ffmpeg is not on PATH")
    run_dir = args.lesson.parent
    problems = mtv_lesson.unrendered(lesson, run_dir, args.tier)
    if problems:
        return common.usage_error(f"run render.py --tier {args.tier} first: " + "; ".join(problems))
    fps = common.TIERS[args.tier][2]
    try:
        scene_t0_s = 0.0
        for scene in lesson["scenes"]:
            for i, beat in enumerate(scene["beats"]):
                beat["render"]["frames"] = beat_frames(run_dir, scene, beat, i == 0, fps, scene_t0_s)
            scene_t0_s += sum(beat["render"]["duration_s"] for beat in scene["beats"])
        record = continuity(lesson, run_dir, args.tier)
    # A video ffmpeg cannot read is bad input to this stage, not a failed gate.
    except RuntimeError as exc:
        return common.usage_error(str(exc))
    common.dump_json(record, run_dir / "frames" / "continuity.json")
    mtv_lesson.mark_done(lesson, "frames", {"pil": "no" if Image is None else "yes"})
    mtv_lesson.save(lesson, args.lesson)
    n_beats = sum(1 for _ in mtv_lesson.beats(lesson))
    failing = sum(not boundary["pass"] for boundary in record["boundaries"])
    return common.verdict(True, f"frames: {n_beats} beats, {len(record['boundaries'])} boundaries, {failing} failing")


if __name__ == "__main__":
    sys.exit(main())
