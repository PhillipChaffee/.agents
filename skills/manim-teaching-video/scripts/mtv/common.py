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
from typing import Any, NamedTuple

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
SYNC_BEAT_TOLERANCE_S = 2 / 15  # measured by M0 Task 9 on 2026-10-26
SYNC_CONTAINER_TOLERANCE_S = 0.5  # measured by M0 Task 9 on 2026-10-26
HANG_TIMEOUT_S = 600  # measured by M0 Task 9 on 2026-10-26
STANDARD_TO_DRAFT_RATIO = 2.00  # measured by M0 Task 9 on 2026-10-26
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


class ErrorRow(NamedTuple):
    """A known render failure: the text that identifies it in ``render.log``, its cause
    (usually a ManimGL habit), the ManimCE fix, and the one sentence a retry carries."""

    pattern: re.Pattern
    gl_idiom: str
    ce_replacement: str
    fix_text: str


# Each pattern is the message text ManimCE 0.22.0 writes at the cited line, so a CE upgrade
# that rewords a message needs that row checked. Order matters only where one log could
# match two rows: match_error returns the first.
ERROR_TABLE: tuple[ErrorRow, ...] = (
    # manim/scene/scene.py:1020-1031
    ErrorRow(
        re.compile(r"Passing Mobject methods to Scene\.play"),
        "self.play(mob.shift, UP)",
        "self.play(mob.animate.shift(UP))",
        "Animate the method through .animate, as in self.play(mob.animate.shift(UP)), instead of passing the"
        " bound method and its arguments to play.",
    ),
    # manim/scene/scene.py:1338
    ErrorRow(
        re.compile(r"Called Scene\.play with no animations"),
        "self.play(*[])",
        "guard empty lists before play",
        "Guard empty lists before play, so a call whose unpacked animation list comes out empty is skipped.",
    ),
    # manim/scene/scene.py:1148-1152 names the parameter its caller passes: play's total run_time,
    # wait's and pause's duration, wait_until's max_time (scene.py:1185, 1269, 1293, 1309); a
    # negative Animation run_time raises at manim/animation/animation.py:176-180 instead.
    ErrorRow(
        re.compile(r"has a (total run_time|duration|max_time) of .* <= 0 seconds|run_time of .* cannot be negative"),
        "a run_time computed from audio came out non-positive",
        "b.until(mark) and b.remaining(), which clamp to one frame",
        "Take every run_time and wait duration inside a beat from b.until(mark) or b.remaining(), which clamp to"
        " one frame, instead of computing it from the audio.",
    ),
    # manim/mobject/mobject.py:2290-2293
    ErrorRow(
        re.compile(r"Trying to restore without having saved"),
        "Restore(m) without m.save_state()",
        "save_and_restore_layout(scene, group)",
        "Make the change inside save_and_restore_layout(scene, group), the context manager that saves the group's"
        " state before it restores it, instead of a bare Restore(m).",
    ),
    # manim/animation/transform.py:436-440 tests hasattr(mobject, "target"), which always holds
    # because every Mobject starts with target None (manim/mobject/mobject.py:116-121), so a
    # missing target becomes Transform's bare Mobject() (transform.py:163-165) and the render
    # fails at manim/mobject/mobject.py:3171-3172 instead; CE 0.22.0 writes only that message.
    ErrorRow(
        re.compile(r"MoveToTarget called on mobject.*'target'|get_point_mobject not implemented for Mobject\b"),
        "MoveToTarget(m) without generate_target()",
        "call m.generate_target(), mutate m.target, then MoveToTarget(m)",
        "Call m.generate_target(), mutate m.target, then play MoveToTarget(m).",
    ),
    # manim/mobject/types/vectorized_mobject.py:2352-2362
    ErrorRow(
        re.compile(r"You can try adding this value into a Group instead"),
        "a non-VMobject inside VGroup",
        "Group(...)",
        "Collect the members in Group(...), since a VGroup accepts only VMobject members.",
    ),
    # manim/animation/animation.py:187,581
    ErrorRow(
        re.compile(r"Animation only works on Mobjects|cannot be converted to an animation"),
        "a list of animations passed unexpanded",
        "unpack with *",
        "Unpack the list of animations with *, as in self.play(*anims), so play receives animations, not a list.",
    ),
    # manim/mobject/mobject.py:3573-3582
    ErrorRow(
        re.compile(r"Animation arguments must be passed before accessing methods"),
        "mob.animate.shift(UP)(run_time=2)",
        "mob.animate(run_time=2).shift(UP)",
        "Pass animation arguments to animate before the method, as in mob.animate(run_time=2).shift(UP).",
    ),
    # manim/mobject/mobject.py:3588-3590
    ErrorRow(
        re.compile(r"Method chaining is currently not supported for overridden animations"),
        "chaining after an overridden animate method",
        "separate play calls",
        "Split the chain into separate play calls, one for each overridden animate method.",
    ),
    # Python's own AttributeError: only MovingCameraScene gives the camera a frame
    # (manim/scene/moving_camera_scene.py:104-121).
    ErrorRow(
        re.compile(r"object has no attribute 'frame'"),
        "self.camera.frame in a plain Scene",
        "NarratedCameraScene and zoom_to",
        "Subclass NarratedCameraScene and move the camera with zoom_to, because a plain scene's camera has no frame.",
    ),
    # manim/mobject/mobject.py:904 names the missing method only for replicate, fix_in_frame and
    # reorient: the property shim above it (mobject.py:867-901) turns a get_ or set_ name into a
    # getter or setter that raises a TypeError on GL arguments or silently succeeds, so
    # check_scenes.py's static ban of every name here is what catches those.
    ErrorRow(
        re.compile(
            r"has no attribute '(set_backstroke|get_grid|replicate|fix_in_frame"
            r"|set_max_width|reorient|set_height|set_width)'"
        ),
        "a GL-only method",
        "the translation rows: set_stroke(BLACK, w, background=True), arrange_in_grid, VGroup(*(m.copy() ...)),"
        " add_fixed_in_frame_mobjects, scale_to_fit_width, set_camera_orientation, mob.height = h, mob.width = w",
        "Replace the GL-only method by its translation row: set_stroke(BLACK, w, background=True) for set_backstroke,"
        " arrange_in_grid for get_grid, VGroup(*(m.copy() ...)) for replicate, add_fixed_in_frame_mobjects for"
        " fix_in_frame, scale_to_fit_width for set_max_width, set_camera_orientation for reorient, and"
        " mob.height = h or mob.width = w for set_height or set_width.",
    ),
    # manim/utils/tex_file_writing.py:215-224
    ErrorRow(
        re.compile(r"latex error converting to"),
        "LaTeX absent, a missing package or a bad formula",
        "fix the formula; a missing package is added only in look.py",
        "Fix the formula, and when the log names a missing LaTeX package, add it only in look.py, never in a scene.",
    ),
    # manim/utils/tex_file_writing.py:246-260
    ErrorRow(
        re.compile(r"dvisvgm.*(not found|at least version 2\.4)"),
        "dvisvgm missing or older than 2.4",
        "install dvisvgm (the D13 package)",
        "Install the dvisvgm system package, version 2.4 or newer, then rerun preflight.py before rendering again.",
    ),
    # manim/mobject/text/text_mobject.py:490 logs this as a warning, which match_error skips, so
    # the row serves the manimce.md table and the retry prompt, never render.log.
    ErrorRow(
        re.compile(r"Font .* not in \["),
        "a font Pango does not have",
        "look.pick_font() chooses from FONT_CANDIDATES",
        "Take the font from look.pick_font(), which chooses an installed one from FONT_CANDIDATES, instead of"
        " naming a font.",
    ),
    # CE writes nothing for this symptom, since it updates only the scene's mobjects
    # (manim/scene/scene.py:409-419); the row exists for the manimce.md table and for the
    # text a retry prompt reports.
    ErrorRow(
        re.compile(r"updaters? (do|did) nothing|updater (never|not) (ran|called)"),
        "a mobject or tracker never added to the scene",
        "self.add(tracker, mob); live_decimal",
        "Add the tracker and the mobject with self.add(tracker, mob) before animating the tracker, or show a"
        " tracked value with live_decimal.",
    ),
    # Written into render.log by render.py when a beat has no section (CE drops an empty
    # section, manim/scene/scene_file_writer.py:321-324).
    ErrorRow(
        re.compile(r"beat .* missing from the section index"),
        "a section with no play or wait",
        "b.remaining() inside the beat; the mixin's exit pad",
        "Give the beat a play or a self.wait(b.remaining()) inside its with block, so its section holds frames,"
        " and let the mixin's exit pad finish it.",
    ),
    # manim/cli/render/commands.py:64
    ErrorRow(
        re.compile(r"--output_file can only be used when rendering exactly one scene"),
        "-o with several scenes",
        "rely on default names",
        "Drop -o and rely on default names, since each scene renders in its own process.",
    ),
    # manim/_config/output.py:63-66
    ErrorRow(
        re.compile(r"--format=webm for transparent video"),
        "-t with MP4",
        "never -t; MP4 only",
        "Never pass -t, since renders are MP4 only and MP4 has no alpha channel.",
    ),
    # manim/constants.py:82-84,89-91; CE logs the second message for a class name the file
    # does not define (manim/utils/module_ops.py:103).
    ErrorRow(
        re.compile(r"There are no scenes inside that module|is not in the script"),
        "the class is missing or construct is misspelled",
        "define scene_class exactly as lesson.json names it",
        "Define scene_class exactly as lesson.json names it, with its method spelled construct.",
    ),
    # manim/mobject/mobject.py:2901
    ErrorRow(
        re.compile(r"Too few rows and columns to fit all"),
        "arrange_in_grid(rows, cols) too small",
        "fix the counts",
        "Fix the counts so that rows times cols in arrange_in_grid covers every submobject.",
    ),
    # manim/mobject/types/vectorized_mobject.py:1660
    ErrorRow(
        re.compile(r"Alpha .* not between 0 and 1"),
        "point_from_proportion out of range",
        "clamp alpha",
        "Clamp alpha to the range 0 to 1 before passing it to point_from_proportion.",
    ),
    # manim/animation/animation.py:616
    ErrorRow(
        re.compile(r"A static Wait animation cannot have a stop condition"),
        "wait(stop_condition=..., frozen_frame=True)",
        "drop one of them",
        "Drop one of them, since a wait takes stop_condition or frozen_frame=True but not both.",
    ),
    # manim/mobject/geometry/shape_matchers.py:62
    ErrorRow(
        re.compile(r"Expected all inputs for parameter mobjects to be a Mobjects"),
        "SurroundingRectangle(point)",
        "pass mobjects",
        "Pass mobjects to SurroundingRectangle, wrapping a bare point in a Dot first.",
    ),
    # CE's pyproject.toml:23; pip's install message, which never reaches render.log.
    ErrorRow(
        re.compile(r"requires-python|Requires-Python|python_requires"),
        "an interpreter outside 3.11 or 3.12",
        "uv venv --python 3.12",
        "Recreate the venv with uv venv --python 3.12; preflight.py is the detector for an interpreter outside"
        " 3.11 or 3.12, so rerun it before rendering.",
    ),
)


# Lines that cannot name the failure, dropped before the search. CE prints an uncaught exception
# with Rich (manim/cli/render/commands.py:123-125), whose panel quotes three source lines around
# every frame, and that source holds some rows' texts beside frames that raise something else:
# row 2's at scene.py:1338 beside the compile_animations call at 1340, row 21's at
# vectorized_mobject.py:1660 beside the empty-points check at 1662. Rich falls back to ASCII
# borders when the output encoding is not UTF-8. A log record below ERROR never fails a render,
# yet an early one would shadow every later row: row 14's font warning, or the INFO record that
# quotes a formula's TeX source (tex_file_writing.py:110).
_RICH_PANEL_LINE = re.compile(r"[│╭╰|+]")
_BELOW_ERROR_RECORD = re.compile(r"(\[[^\]]*\])? *(DEBUG|INFO|WARNING) ")
# A RichHandler record's first line: the time column (blank when the time repeats), the level,
# the message, and the right-aligned path:line column, which continuation lines leave out.
_LOG_RECORD = re.compile(r"(\[[^\]]*\])? *(DEBUG|INFO|WARNING|ERROR|CRITICAL) ")
_PATH_COLUMN = re.compile(r" +\S+:\d+ *$")


def _logical_lines(log_text: str) -> list[str]:
    """Undo Rich's wrapping, so a message is one line whatever the console width.

    render.log is not a terminal, so Rich wraps at COLUMNS, else 80 columns: an exception
    message continues at column 0, a log record continues on lines indented to its message
    column, and a pattern can straddle either break. A blank or panel line ends both.
    """
    lines: list[str] = []
    follow: bool | None = None  # whether indented (True) or column-0 (False) lines continue lines[-1]
    for line in log_text.splitlines():
        if not line.strip() or _RICH_PANEL_LINE.match(line):
            follow = None
        elif _LOG_RECORD.match(line):
            lines.append(_PATH_COLUMN.sub("", line))
            follow = True
        elif follow is not None and follow == line[0].isspace():
            lines[-1] = f"{lines[-1].rstrip()} {line.strip()}"
        else:
            lines.append(line)
            follow = None if line[0].isspace() else False
    return lines


def match_error(log_text: str) -> ErrorRow | None:
    failure_text = "\n".join(line for line in _logical_lines(log_text) if not _BELOW_ERROR_RECORD.match(line))
    for row in ERROR_TABLE:
        if row.pattern.search(failure_text):
            return row
    return None


# The names check_scenes.py rejects in a generated scenes file, each mapped to the fix its
# finding carries: every ManimGL name that ManimCE 0.22.0 lacks (or keeps for the OpenGL
# renderer and interactive use only, as with get_width and embed), mapped to its ManimCE
# replacement, plus the names through which a scene could read a file or the network, since
# a render loads no raster asset, downloads nothing and reaches its lesson only through
# load_lesson.
BANNED_NAMES: dict[str, str] = {
    "manimlib": "from manim import *",
    "ImageMobject": "vector mobjects; a render loads no raster image",
    "open": "self.load_lesson(scene_id), which finds lesson.json through MTV_LESSON",
    "Path": "self.load_lesson(scene_id), which finds lesson.json through MTV_LESSON",
    "requests": "values computed in the scene; a render has no network access",
    "urllib": "values computed in the scene; a render has no network access",
    "InteractiveScene": "NarratedScene, NarratedCameraScene or Narrated3DScene, as scene_kind says",
    "CONFIG": "class attributes or __init__ keyword arguments",
    "TexMobject": "MathTex",
    "TextMobject": "Tex",
    "TexText": "Tex",
    "OldTex": 'MathTex("a", "+", "b", arg_separator=" ")',
    "OldTexText": 'Tex("word", "word", arg_separator="")',
    "ShowCreation": "Create",
    "ShowCreationThenDestruction": "ShowPassingFlash(m, time_width=1.0)",
    "ShowCreationThenFadeOut": "Succession(Create(m), FadeOut(m))",
    "ShowCreationThenDestructionAround": "Circumscribe(m)",
    "ShowPassingFlashAround": "Circumscribe(m)",
    "FlashAround": "Circumscribe(m)",
    "FlashUnder": "ShowPassingFlash(Underline(m), time_width=1.0)",
    "CircleIndicate": "Circumscribe(m, shape=Circle)",
    "VShowPassingFlash": "ShowPassingFlash(m, time_width=0.1)",
    "VFadeIn": "FadeIn",
    "VFadeOut": "FadeOut",
    "VFadeInThenOut": "Succession(FadeIn(m), FadeOut(m))",
    "FadeInFromPoint": "FadeIn(m, target_position=point, scale=0.1)",
    "FadeOutToPoint": "FadeOut(m, target_position=point, scale=0.1)",
    "WiggleOutThenIn": "Wiggle(m)",
    "CountInFrom": "num.set_value(source), then ChangeDecimalToValue(num, target)",
    "TurnInsideOut": "none in ManimCE; Transform(m, target) or FadeIn(m)",
    "FlashyFadeIn": "none in ManimCE; FadeIn(m)",
    "TexMatrix": "Matrix",
    "GlowDot": "Dot inside concentric Circles of decreasing fill opacity",
    "GlowDots": "VGroup of Dot",
    "DotCloud": "VGroup of Dot",
    "TrueDot": "Dot",
    "Checkmark": r'Tex(r"\checkmark")',
    "Exmark": r'MathTex(r"\times")',
    "PiCreature": "none in ManimCE, and 3b1b's drawings are not copied; leave the character out",
    "SpeechBubble": "question_caption(target, text)",
    "ThoughtBubble": "question_caption(target, text)",
    "TexturedSurface": "Surface with fill_color or checkerboard_colors; a render loads no texture image",
    "ParametricSurface": "Surface(func, u_range, v_range, resolution)",
    "Square3D": "Square().set_shade_in_3d()",
    "VCube": "Cube(side_length, fill_opacity)",
    "VPrism": "Prism",
    "FullScreenFadeRectangle": "FullScreenRectangle(fill_color=BLACK, fill_opacity=0.7, stroke_width=0)",
    "set_backstroke": "set_stroke(BLACK, width, background=True)",
    "get_grid": "arrange_in_grid(rows, cols) on a VGroup of copies",
    "replicate": "VGroup(*(mob.copy() for _ in range(n)))",
    "fix_in_frame": "self.add_fixed_in_frame_mobjects(mob) in a Narrated3DScene",
    "set_max_width": "if mob.width > w: mob.scale_to_fit_width(w)",
    "set_max_height": "if mob.height > h: mob.scale_to_fit_height(h)",
    "set_min_width": "if mob.width < w: mob.scale_to_fit_width(w)",
    "reorient": "self.set_camera_orientation or self.move_camera, in radians, in a Narrated3DScene",
    "set_height": "mob.scale_to_fit_height(h), or mob.height = h",
    "set_width": "mob.scale_to_fit_width(w), or mob.width = w",
    "get_width": "mob.width",
    "get_height": "mob.height",
    "make_number_changeable": "a DecimalNumber or live_decimal(tracker) placed with move_to(part)",
    "select_part": 'tex.get_part_by_tex("x") on an isolated substring',
    "select_parts": 'tex.get_part_by_tex("x") on an isolated substring',
    "add_coordinate_labels": "add_coordinates()",
    "get_graph": "axes.plot(f, x_range=...)",
    "get_v_line_to_graph": "axes.get_vertical_line(axes.i2gp(x, graph))",
    "get_area_under_graph": "axes.get_area(graph, x_range=...)",
    "set_floor_plane": "none in ManimCE; drop the call",
    "embed": "none in a ManimCE render; drop the call",
    "checkpoint_paste": "none in ManimCE; drop the call",
    "time_span": "delayed(anim, start_s, total_s), or rate_func=squish_rate_func(smooth, a / T, b / T) with run_time=T",
    "isolate": "substrings_to_isolate=[...] on MathTex, or {{ x }} groups",
}
