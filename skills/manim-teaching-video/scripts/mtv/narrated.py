"""Beat timing for generated scenes: narration fixes each beat's length and the scene follows it.

A scenes file wraps each beat in ``with self.beat(beat_id) as b:`` and times its animations
with ``b.until(mark)`` and ``b.remaining()``. On exit the mixin pads the beat to its narrated
end and appends one JSON line to the run log that render.py and verify.py read.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import common, lesson

try:
    from manim import DL, UR, MovingCameraScene, Scene, ThreeDScene, ValueTracker, config

    MANIM_AVAILABLE = True
    # Mobjects CE keeps in the scene that never draw: the 3D camera's angle trackers.
    _UNDRAWN_TYPES: tuple[type, ...] = (ValueTracker,)
except ImportError:
    # The self-test drives the mixin through a stand-in scene where ManimCE is absent.
    MANIM_AVAILABLE = False
    _UNDRAWN_TYPES = ()


def _frames_to_reach(t_s: float, fps: float) -> int:
    """The whole frames it takes to reach ``t_s``; a time within float noise of a frame boundary is on it."""
    return math.ceil(t_s * fps - common.FRAME_SLACK)


@dataclass
class Beat:
    """One beat's narrated timing, read against the scene clock while the beat's body runs."""

    beat_id: str
    narration: str
    duration: float
    tail_s: float
    marks_s: dict[str, float]
    enter_s: float
    target_end: float
    fps: float
    clock: Callable[[], float]

    # Both run times are at least one frame because CE rejects a run_time that is not
    # positive (CE manim/scene/scene.py:1148-1153), which a late animation would otherwise pass.
    def until(self, mark: str, lead: float = common.DEFAULT_LEAD_S) -> float:
        """The run time that ends an animation ``lead`` seconds before ``mark`` is spoken."""
        return max(self.marks_s[mark] - lead - (self.clock() - self.enter_s), 1 / self.fps)

    def remaining(self) -> float:
        """The run time that ends an animation on the first frame at or after the beat's narration and tail end."""
        frames = max(_frames_to_reach(self.target_end - self.clock(), self.fps), 1)
        # CE draws one frame per np.arange(0, run_time, 1/fps) step (CE manim/scene/scene.py:1128-1129),
        # where a whole number of frames can divide out a hair above itself (23/15 s draws 24 frames
        # at 15 fps); half a frame short draws exactly ``frames``. A single frame divides exactly, and
        # CE warns below it (1158-1165). A static wait rounds down instead
        # (CE manim/renderer/cairo_renderer.py:221-225), ending a frame early, which the exit pad fills.
        return max(frames - 0.5, 1) / self.fps


class NarratedMixin:
    """Times a ManimCE scene's beats by their narration; mixed in ahead of the scene class.

    Beat ends count from the scene start, so a scenes file sets up anything shown before its
    first beat with ``self.add``: a ``play`` or ``wait`` there would shorten the first beat.
    """

    def load_lesson(self, scene_id: str, lesson_path: Path | None = None) -> None:
        # A generated scenes file may not open files, so render.py names the lesson in MTV_LESSON.
        path = lesson_path or os.environ.get("MTV_LESSON")
        if not path:
            raise ValueError("no lesson to load: pass lesson_path or set MTV_LESSON")
        self._mtv_scene = lesson.scene_by_id(lesson.load(Path(path)), scene_id)
        self._mtv_beats = {entry["id"]: entry for entry in self._mtv_scene["beats"]}
        self._mtv_cursor = 0.0
        self._mtv_run_log = os.environ.get("MTV_RUN_LOG")
        if MANIM_AVAILABLE:
            # Imported here because look.py needs ManimCE and this module must load without it.
            from . import look

            look.apply(self)

    @contextlib.contextmanager
    def beat(self, beat_id: str) -> Iterator[Beat]:
        entry = self._mtv_beats[beat_id]
        fps = self._fps()
        # The section name is how render.py and verify.py find this beat in CE's section index
        # (CE manim/scene/scene.py:378-388); the subcaption spans the narration (1726-1766).
        self.next_section(beat_id)
        self.add_subcaption(entry["narration"], duration=entry["duration_s"])
        # enter_s and exit_s read CE's clock, which play keeps on the frames the section index counts.
        timing = Beat(
            beat_id=beat_id,
            narration=entry["narration"],
            duration=entry["duration_s"],
            tail_s=entry["tail_s"],
            marks_s=entry["marks_s"],
            enter_s=self.time,  # CE manim/scene/scene.py:286-288
            # Cumulative from the scene start, so a pad rounded to whole frames in one beat is
            # made up in the next instead of adding up over the scene.
            target_end=self._mtv_cursor + entry["duration_s"] + entry["tail_s"],
            fps=fps,
            clock=lambda: self.time,
        )
        # Not in a try/finally: a beat whose body raised is neither padded nor logged, so
        # render.py finds it missing and surfaces the traceback.
        yield timing
        pad_s = timing.target_end - self.time
        # CE's clock moves in whole frames, so a beat ends no sooner than the first frame at or after
        # its target, where a body ending on b.remaining() lands: only time past that frame overruns,
        # and a residue within common.CLOCK_EPSILON_S of it is float error.
        past_frame_s = self.time - _frames_to_reach(timing.target_end, fps) / fps
        overrun_s = past_frame_s if past_frame_s > common.CLOCK_EPSILON_S else 0.0
        # A clock already on the narrated end needs no pad; the one-frame floor would add a frame.
        if abs(pad_s) > common.CLOCK_EPSILON_S:
            self.wait(max(pad_s, 1 / fps))  # CE manim/scene/scene.py:1242-1283
        if self._mtv_run_log:
            # Opened per beat so each line lands at once; render.py's hang detector watches it grow.
            with open(self._mtv_run_log, "a", encoding="utf-8") as run_log:
                run_log.write(json.dumps(self._log_line(timing, self.time, overrun_s)) + "\n")
        self._mtv_cursor = timing.target_end

    def play(self, *args: Any, **kwargs: Any) -> None:
        """CE's play, with the clock kept on the frames written when CE reuses a cached segment.

        A reused segment holds the whole frames it was first rendered with, but CE advances the
        clock by the exact run time (CE manim/renderer/cairo_renderer.py:104-110). Left alone,
        every reused animation would move the run log, the pads and the subcaptions up to a frame
        off the section index, and the drift would add up over a re-rendered scene. wait comes
        through here too (CE manim/scene/scene.py:1269-1275).
        """
        start_s = self.time
        super().play(*args, **kwargs)
        # CE leaves this set only after a segment it did not render (cairo_renderer.py:76-110): a
        # cache hit, or a skipped section or animation range, which render.py never asks for.
        if self.renderer.skip_animations:
            self.renderer.time = self._rendered_clock(start_s)

    def _rendered_clock(self, start_s: float) -> float:
        """The clock CE leaves after rendering the segment just played, from ``start_s``.

        The frame counts and the per-frame sums are CE's own, so a replayed pad gets the same run
        time to the last bit, hashes the same, and stays cached.
        """
        dt = 1 / self._fps()
        # self.duration is the play's run time after CE's one-frame floor (CE manim/scene/scene.py:1348).
        if self.is_current_animation_frozen_frame():
            # A static wait is one frame repeated (CE manim/renderer/cairo_renderer.py:210,221-225).
            return start_s + int(self.duration / dt) * dt
        clock = start_s
        # One frame per np.arange(0, run_time, dt) step (CE manim/scene/scene.py:1128-1129),
        # each advancing the clock by dt (CE manim/renderer/cairo_renderer.py:210).
        for _ in range(math.ceil(self.duration / dt)):
            clock += dt
        return clock

    def _fps(self) -> float:
        return config.frame_rate if MANIM_AVAILABLE else getattr(self, "frame_rate", 15.0)

    def _boxes(self) -> list[dict]:
        """Scene-unit bounding boxes of the top-level mobjects, for the frame critic's clipping check.

        The points test covers the whole family because a group holds no points of its own
        (CE manim/mobject/mobject.py:2360-2366); a mobject with none anywhere is skipped, since
        CE puts its corners at the origin (2410-2413), where nothing is drawn. Camera bookkeeping
        is skipped too: CE adds the moving camera's frame to the scene when it animates and the
        3D camera's angle trackers when they rotate, and a tracker's one point sits at its value,
        so a long orbit would read as a mobject clipped off the frame.
        """
        boxes = []
        frame = getattr(getattr(self, "camera", None), "frame", None)
        for mobject in self.mobjects:
            if mobject is frame or isinstance(mobject, _UNDRAWN_TYPES):
                continue
            if len(mobject.get_all_points()) == 0:
                continue
            x0, y0 = mobject.get_corner(DL)[:2]  # CE manim/mobject/mobject.py:2428
            x1, y1 = mobject.get_corner(UR)[:2]
            boxes.append({"name": type(mobject).__name__, "x0": float(x0), "y0": float(y0),
                          "x1": float(x1), "y1": float(y1)})
        return boxes

    def _log_line(self, beat: Beat, exit_s: float, overrun_s: float) -> dict:
        # Spec 6.10's key order, which json.dumps keeps in the run.log line; readers look keys up by name.
        return {
            "beat": beat.beat_id,
            "enter_s": beat.enter_s,
            "exit_s": exit_s,
            "audio_s": beat.duration,
            "tail_s": beat.tail_s,
            "overrun_s": overrun_s,
            "boxes": self._boxes(),
        }


if MANIM_AVAILABLE:
    # The three bases a scenes file may subclass; check_scenes.py matches each to a scene_kind.

    class NarratedScene(NarratedMixin, Scene):
        """A flat narrated scene."""

    class NarratedCameraScene(NarratedMixin, MovingCameraScene):  # CE manim/scene/moving_camera_scene.py:104-121
        """A narrated scene whose camera frame can move and zoom (zoom_to)."""

    class Narrated3DScene(NarratedMixin, ThreeDScene):  # CE manim/scene/three_d_scene.py:31
        """A narrated 3D scene with an orbiting camera (orbit_with_hud)."""
