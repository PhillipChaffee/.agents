"""Beat timing for generated scenes: narration fixes each beat's length and the scene follows it.

A scenes file wraps each beat in ``with self.beat(beat_id) as b:`` and times its animations
with ``b.until(mark)`` and ``b.remaining()``. On exit the mixin pads the beat to its narrated
end and appends one JSON line to the run log that render.py and verify.py read.
"""

from __future__ import annotations

import contextlib
import json
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from . import common, lesson

try:
    from manim import DL, UR, MovingCameraScene, Scene, ThreeDScene, config

    MANIM_AVAILABLE = True
except ImportError:
    # The self-test drives the mixin through a stand-in scene where ManimCE is absent.
    MANIM_AVAILABLE = False


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
        """The run time left until the beat's narration and tail end."""
        return max(self.target_end - self.clock(), 1 / self.fps)


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
        overrun_s = max(self.time - timing.target_end, 0.0)
        self.wait(max(timing.target_end - self.time, 1 / fps))  # CE manim/scene/scene.py:1242-1283
        if self._mtv_run_log:
            # Opened per beat so each line lands at once; render.py's hang detector watches it grow.
            with open(self._mtv_run_log, "a", encoding="utf-8") as run_log:
                run_log.write(json.dumps(self._log_line(timing, self.time, overrun_s)) + "\n")
        self._mtv_cursor = timing.target_end

    def _fps(self) -> float:
        return config.frame_rate if MANIM_AVAILABLE else getattr(self, "frame_rate", 15.0)

    def _boxes(self) -> list[dict]:
        """Scene-unit bounding boxes of the top-level mobjects, for the frame critic's clipping check.

        The points test covers the whole family because a group holds no points of its own
        (CE manim/mobject/mobject.py:2360-2366); a mobject with none anywhere is skipped, since
        CE puts its corners at the origin (2410-2413), where nothing is drawn.
        """
        boxes = []
        for mobject in self.mobjects:
            if len(mobject.get_all_points()) == 0:
                continue
            x0, y0 = mobject.get_corner(DL)[:2]  # CE manim/mobject/mobject.py:2428
            x1, y1 = mobject.get_corner(UR)[:2]
            boxes.append({"name": type(mobject).__name__, "x0": float(x0), "y0": float(y0),
                          "x1": float(x1), "y1": float(y1)})
        return boxes

    def _log_line(self, beat: Beat, exit_s: float, overrun_s: float) -> dict:
        # render.py copies these keys in this order into the beat's render.log object.
        return {
            "beat": beat.beat_id,
            "enter_s": beat.enter_s,
            "exit_s": exit_s,
            "audio_s": beat.duration,
            "tail_s": beat.tail_s,
            "overrun_s": overrun_s,
            "boxes": self._boxes(),
        }
