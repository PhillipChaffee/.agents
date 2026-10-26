"""Standard-library self-test for the manim-teaching-video scripts.

Optional dependencies and tools are looked up inside the case that needs them, so a
machine without them still runs every other case and exits 0.
"""

from __future__ import annotations

import argparse
import configparser
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
import wave
from pathlib import Path
from types import ModuleType
from typing import NoReturn

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"

# The self-test writes only to its scratch directories, so neither it nor a script
# that run_script starts may leave bytecode caches in the skill's scripts/ tree.
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS_DIR))

import check_scenes  # noqa: E402
import mtv.common as common  # noqa: E402
import mtv.lesson as mtv_lesson  # noqa: E402
import mtv.tts as tts  # noqa: E402
import narrate  # noqa: E402
import storyboard_check  # noqa: E402


def _skip(fixture: str, dependency: str) -> NoReturn:
    message = f"SKIP {fixture}: {dependency} not available"
    print(message)
    raise unittest.SkipTest(message)


def require(module: str, fixture: str) -> ModuleType:
    try:
        return importlib.import_module(module)
    except ImportError:
        _skip(fixture, module)


def require_tool(tool: str, fixture: str) -> str:
    path = common.which(tool)
    if path is None:
        _skip(fixture, tool)
    return path


def run_script(
    name: str, *args: str, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    full_env = dict(os.environ if env is None else env)
    full_env["PYTHONPATH"] = str(SCRIPTS_DIR)
    full_env["PYTHONDONTWRITEBYTECODE"] = "1"
    return common.run_cmd([sys.executable, str(SCRIPTS_DIR / f"{name}.py"), *args], env=full_env, cwd=cwd)


class Scratch(tempfile.TemporaryDirectory):
    """A temporary directory owned by one test class, with its location as ``path``."""

    def __init__(self) -> None:
        super().__init__(prefix="mtv-selftest-")
        self.path = Path(self.name)


def example_run_dir(parent: Path) -> Path:
    """A new run directory under ``parent`` holding a copy of the example lesson.

    unittest runs a class's tests in name order, so a run directory shared between them
    would let one test's leftovers decide another's result.
    """
    run_dir = Path(tempfile.mkdtemp(dir=parent)) / "run"
    run_dir.mkdir()
    shutil.copyfile(ASSETS_DIR / "lesson.example.json", run_dir / "lesson.json")
    return run_dir


# ManimCE is absent where the self-test runs, so the scripts under test find this stand-in
# first on PATH. Its dry run fails for a class whose name contains Bad, so a test can take
# the failing path with a scenes file that is otherwise clean.
FAKE_MANIM_SOURCE = r'''"""A stand-in for ManimCE's manim command that records each call in calls.jsonl beside it."""
import json
import os
import sys
from pathlib import Path

argv = sys.argv[1:]
with open(Path(__file__).resolve().parent / "calls.jsonl", "a", encoding="utf-8") as calls:
    calls.write(json.dumps(argv) + "\n")
if "--version" in argv:
    print("Manim Community v0.22.0")
    sys.exit(0)
if "--dry_run" in argv:
    # A real dry run still executes construct, whose load_lesson reads MTV_LESSON.
    if not os.environ.get("MTV_LESSON"):
        sys.exit("ValueError: MTV_LESSON is not set")
    if "Bad" in argv[-1]:
        sys.exit(f"ValueError: {argv[-1]} failed its dry run")
    sys.exit(0)
sys.exit("fake manim: no render branch")
'''

# The example lesson's two scene classes, each with the base its flat scene_kind needs.
CLEAN_TWO_CLASS_SOURCE = """from manim import *
from mtv.narrated import NarratedScene


class S01WorkingThing(NarratedScene):
    def construct(self):
        pass


class S02OneNeuron(NarratedScene):
    def construct(self):
        pass
"""


def write_fake_manim(bin_dir: Path) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    path = bin_dir / "manim"
    path.write_text(f"#!{sys.executable}\n{FAKE_MANIM_SOURCE}", encoding="utf-8")
    path.chmod(0o755)
    return path


def env_with_fake_manim(bin_dir: Path) -> dict[str, str]:
    """This process's environment with ``bin_dir`` first on PATH; the fake manim there
    records every call's argv as one JSON line in ``bin_dir/calls.jsonl``."""
    return {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}


class ExampleLessonCase(unittest.TestCase):
    """Gives each test its own run directory holding the example lesson, under one class scratch."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def setUp(self):
        self.run_dir = example_run_dir(self.scratch.path)
        self.lesson_path = self.run_dir / "lesson.json"


class TestVocabularies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def test_vocabulary_sizes(self):
        self.assertEqual(len(common.TECHNIQUE_TAGS), 28)
        self.assertEqual(len(common.MOVES), 8)
        self.assertEqual(len(common.SCENE_KINDS_CORPUS), 8)
        self.assertEqual(common.RUNTIME_SCENE_KINDS, ("flat", "camera", "3d"))
        self.assertEqual(common.OPENING_STATES, ("black", "continue", "cut"))
        self.assertEqual(len(common.IDIOM_TAGS), 13)
        self.assertEqual(len(common.PATTERN_TAGS), 16)
        self.assertEqual(len(common.MOVE_TAGS), 8)

    def test_vocabulary_targets_in_technique_tags(self):
        for target in common.IDIOM_TAGS.values():
            self.assertIn(target, common.TECHNIQUE_TAGS)
        for targets in common.PATTERN_TAGS.values():
            for target in targets:
                self.assertIn(target, common.TECHNIQUE_TAGS)
        for target in common.MOVE_TAGS.values():
            self.assertIn(target, common.TECHNIQUE_TAGS)

    def test_color_sets_cover_both_gray_spellings(self):
        # CE defines 89 color constants and spells every gray both ways; a color set
        # that knows only one spelling treats identical colors differently.
        self.assertEqual(len(common.COLOR_NAMES), 89)
        self.assertLessEqual(common.NEUTRAL_COLORS, common.COLOR_NAMES)
        for name in common.COLOR_NAMES:
            twin = name.replace("GREY", "GRAY") if "GREY" in name else name.replace("GRAY", "GREY")
            self.assertIn(twin, common.COLOR_NAMES)
            self.assertEqual(name in common.NEUTRAL_COLORS, twin in common.NEUTRAL_COLORS, name)

    def test_normalize_words_splits_and_expands(self):
        self.assertEqual(common.normalize_words("Eighty-four, weights!"), ["eighty", "four", "weights"])
        words = common.normalize_words("Here is 784.")
        try:
            import num2words  # noqa: F401
            self.assertEqual(words, ["here", "is", "seven", "hundred", "and", "eighty", "four"])
        except ImportError:
            self.assertEqual(words, ["here", "is", "784"])

    def test_thirteen_word_runs(self):
        text = " ".join(f"w{i}" for i in range(15))
        self.assertEqual(len(common.thirteen_word_runs(text)), 3)

    def test_dump_json_sorted_indented_newline(self):
        path = Path(self.scratch.path) / "x.json"
        common.dump_json({"b": 1, "a": [1, 2]}, path)
        self.assertEqual(path.read_text(), '{\n  "a": [\n    1,\n    2\n  ],\n  "b": 1\n}\n')

    def test_exemplar_id_patterns(self):
        self.assertTrue(common.CORPUS_EXEMPLAR_ID.search("see aircAruvnKk-s09-b03 here"))
        self.assertTrue(common.ORIGINAL_EXEMPLAR_ID.search("orig-what-a-neuron-computes-s02-b01"))
        self.assertFalse(common.CORPUS_EXEMPLAR_ID.search("beat s01-b01 of scene s01"))

    def test_cfg_tiers(self):
        for tier, (w, h, fps) in common.TIERS.items():
            cfg = configparser.ConfigParser()
            cfg.read(ASSETS_DIR / f"manim.cfg.{tier}")
            self.assertEqual(cfg["CLI"]["pixel_width"], str(w))
            self.assertEqual(cfg["CLI"]["pixel_height"], str(h))
            self.assertEqual(cfg["CLI"]["frame_rate"], str(fps))
            self.assertEqual(cfg["CLI"]["background_color"], "BLACK")
            self.assertEqual(cfg["CLI"]["save_sections"], "True")
            self.assertEqual(cfg["CLI"]["disable_caching_warning"], "True")
            self.assertEqual(cfg["CLI"]["tex_template"], "")

    def test_requirements_pins(self):
        text = (SCRIPTS_DIR / "requirements.txt").read_text()
        for pin in ("manim==0.22.0", "soundfile==0.14.0", "elevenlabs==2.74.1", "num2words==0.5.14", "Pillow==13.0.0"):
            self.assertIn(pin, text)
        self.assertEqual((SCRIPTS_DIR / "requirements-kokoro.txt").read_text().strip(), "kokoro==0.9.4")


class TestErrorTable(unittest.TestCase):
    def test_error_table_rows(self):
        self.assertEqual(len(common.ERROR_TABLE), 24)
        for row in common.ERROR_TABLE:
            self.assertIsInstance(row.pattern, re.Pattern)
            self.assertNotIn("\\|", row.pattern.pattern)
            for field in (row.gl_idiom, row.ce_replacement, row.fix_text):
                self.assertTrue(field.strip())
        self.assertTrue(common.ERROR_TABLE[6].pattern.search("TypeError: cannot be converted to an animation"))
        self.assertTrue(common.ERROR_TABLE[12].pattern.search("You need dvisvgm at least version 2.4"))
        self.assertIn("preflight.py", common.ERROR_TABLE[23].fix_text)

    def test_match_error_first_row(self):
        log = "Traceback\nTypeError: Passing Mobject methods to Scene.play is no longer supported. Use Mobject.animate instead.\n"
        self.assertEqual(common.match_error(log).ce_replacement, "self.play(mob.animate.shift(UP))")
        self.assertIsNone(common.match_error("File ready at out.mp4"))
        self.assertEqual(common.match_error("ValueError: latex error converting to dvi. See log output above").gl_idiom,
                         common.ERROR_TABLE[11].gl_idiom)

    def test_each_row_matches_its_own_message(self):
        # The text each failure writes to render.log: CE 0.22.0's message at the row's cited
        # line, render.py's line for row 16, pip's for row 24, the symptom wording for row 15.
        # A mistyped pattern, or an earlier row that shadows a later one, fails here. Row 14's
        # text is a CE warning, which match_error skips because no warning fails a render. Row 5's
        # first text is its cited line's, which CE 0.22.0 never reaches; the second is what it writes.
        samples = (
            (1, "TypeError: Passing Mobject methods to Scene.play is no longer supported."
                " Use Mobject.animate instead."),
            (2, "ValueError: Called Scene.play with no animations"),
            (3, "ValueError: S01Intro.play() has a total run_time of 0 <= 0 seconds which Manim cannot render."
                " The total run_time must be a positive number."),
            (3, "ValueError: S01Intro.wait() has a duration of -0.2 <= 0 seconds which Manim cannot render."
                " The duration must be a positive number."),
            (3, "ValueError: S01Intro.wait_until() has a max_time of 0 <= 0 seconds which Manim cannot render."
                " The max_time must be a positive number."),
            (3, "ValueError: The run_time of FadeIn cannot be negative. The given value was -0.2."),
            (4, "Exception: Trying to restore without having saved"),
            (5, "ValueError: MoveToTarget called on mobjectwithout attribute 'target'"),
            (5, "NotImplementedError: get_point_mobject not implemented for Mobject"),
            (6, "TypeError: Only values of type VMobject can be added as submobjects of VGroup, but the value"
                " Group (at index 0 of parameter 0) is of type Group."
                " You can try adding this value into a Group instead."),
            (7, "TypeError: Animation only works on Mobjects"),
            (7, "TypeError: Object [FadeIn(Square)] cannot be converted to an animation"),
            (8, "ValueError: Animation arguments must be passed before accessing methods"
                " and can only be passed once"),
            (9, "NotImplementedError: Method chaining is currently not supported for overridden animations"),
            (10, "AttributeError: 'Camera' object has no attribute 'frame'"),
            (11, "AttributeError: Square object has no attribute 'replicate'"),
            (12, "ValueError: latex error converting to dvi. See log output above or the log file: media/Tex/a.log"),
            (13, "ValueError: Your installation does not support converting .dvi files to SVG."
                 " Consider updating dvisvgm to at least version 2.4."),
            (15, "the updaters did nothing"),
            (16, "mtv: beat s01-b02 missing from the section index"),
            (17, "ValueError: --output_file can only be used when rendering exactly one scene."
                 " Remove --write_all or select a single scene."),
            (18, "ValueError: MP4 output does not support an alpha channel. Use --format=mov or --format=webm for"
                 " transparent video."),
            (19, "   There are no scenes inside that module"),
            (19, "   NeuronScene is not in the script"),
            (20, "ValueError: Too few rows and columns to fit all"),  # CE's last word is misspelled
            (21, "ValueError: Alpha 1.5 not between 0 and 1."),
            (22, "ValueError: A static Wait animation cannot have a stop condition."),
            (23, "TypeError: Expected all inputs for parameter mobjects to be a Mobjects"),
            (24, "ERROR: Ignored the following versions that require a different python version:"
                 " 0.22.0 Requires-Python >=3.11"),
        )
        self.assertEqual({row for row, _ in samples}, set(range(1, 25)) - {14})
        for row, message in samples:
            with self.subTest(row=row, message=message):
                self.assertIs(common.match_error(message), common.ERROR_TABLE[row - 1])
        font_warning = "[10/26/26 02:48:56] WARNING  Font Comic Sans not in ['DejaVu Sans', 'Noto Sans']."
        self.assertTrue(common.ERROR_TABLE[13].pattern.search(font_warning))
        self.assertIsNone(common.match_error(font_warning))

    def test_match_error_ignores_quoted_source_and_warnings(self):
        # Lines from Rich 15's rendering of CE 0.22.0 tracebacks, as print_exception draws them
        # (manim/cli/render/commands.py:124), with frame headers and other frames left out: each
        # panel quotes CE source that holds row 2's or row 21's text beside the frame that failed,
        # and the font warning holds row 14's.
        def panel(*source_lines: str) -> tuple[str, ...]:
            top = "╭" + "─" * 31 + " Traceback (most recent call last) " + "─" * 32 + "╮"
            return (top, *(f"│ {line:<96} │" for line in source_lines), "╰" + "─" * 98 + "╯")

        warning = "[10/26/26 02:48:56] WARNING  Font Comic Sans not in ['DejaVu Sans', 'Noto Sans']."
        play_mobject = (
            warning,
            *panel('❱ 581 │   raise TypeError(f"Object {anim} cannot be converted to an animation")'),
            "TypeError: Object Square cannot be converted to an animation",
            "",
            "The above exception was the direct cause of the following exception:",
            "",
            *panel(
                "  1337 │   │   if len(animations) == 0:",
                '  1338 │   │   │   raise ValueError("Called Scene.play with no animations")',
                "  1339 │   │",
                "❱ 1340 │   │   self.animations = self.compile_animations(*animations, **play_kwargs)",
            ),
            "TypeError: Unexpected argument Square passed to Scene.play().",
        )
        self.assertIs(common.match_error("\n".join(play_mobject)), common.ERROR_TABLE[6])
        empty_points = (
            warning,
            *panel(
                '  1660 │   │   │   raise ValueError(f"Alpha {alpha} not between 0 and 1.")',
                "  1661 │   │",
                "❱ 1662 │   │   self._throw_error_if_no_points()",
            ),
            "ValueError: VMobject has no points, but a method which requires points was called",
        )
        self.assertIsNone(common.match_error("\n".join(empty_points)))
        # Rich's ASCII borders, drawn when the output encoding is not UTF-8.
        ascii_line = '|   1660             raise ValueError(f"Alpha {alpha} not between 0 and 1.")   |'
        self.assertIsNone(common.match_error(ascii_line))

    def test_match_error_undoes_rich_wrapping(self):
        # Lines from real CE 0.22.0 render.logs at Rich's 80 columns (stdout is a file and COLUMNS
        # is unset), with the INFO records before the failure left out. Each pattern straddles a
        # break: an exception message continues at column 0, a log record on lines indented to
        # its message column.
        vgroup = (
            "TypeError: Only values of type VMobject can be added as submobjects of VGroup, ",
            "but the value Group (at index 0 of parameter 0) is of type Group. You can try ",
            "adding this value into a Group instead.",
        )
        missing_class = (
            "                    ERROR                                      module_ops.py:103",
            "                                NeuronLayerScene is not in the                  ",
            "                             script                                             ",
            "                                                                                ",
            "1: N01EmptyPoints",
        )
        no_scenes = (
            "                    ERROR                                       module_ops.py:90",
            "                                There are no scenes inside that                 ",
            "                             module                                             ",
        )
        for row, lines in ((6, vgroup), (19, missing_class), (19, no_scenes)):
            with self.subTest(row=row, first=lines[0]):
                self.assertIs(common.match_error("\n".join(lines)), common.ERROR_TABLE[row - 1])
        # A record joined whole still cannot name the failure when it is below ERROR: this INFO
        # record (tex_file_writing.py:110, its formula and path edited) would complete row 13's pattern.
        tex_record = (
            "                    INFO     Writing                     tex_file_writing.py:110",
            "                             \\special{dvisvgm:raw <g                            ",
            "                             id='unique000'>}\\text{not                          ",
            "                             found}\\special{dvisvgm:raw </g>} to                ",
            "                             media/Tex/bdbd54e1f23b9d16.tex                     ",
            "ValueError: Alpha 1.5 not between 0 and 1.",
        )
        self.assertIs(common.match_error("\n".join(tex_record)), common.ERROR_TABLE[20])

    def test_error_table_matches_manimce_reference(self):
        ref = SKILL_DIR / "references" / "manimce.md"
        if not ref.exists():
            print("SKIP error table: references/manimce.md not present (M2 writes it)")
            raise unittest.SkipTest("references absent")
        # The table sets code in backticks, which the rows' plain-text fields do not carry.
        text = ref.read_text().replace("`", "")
        for row in common.ERROR_TABLE:
            self.assertIn(row.gl_idiom, text)
            self.assertIn(row.ce_replacement, text)


class TestLessonSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def test_schema_accept(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        self.assertEqual(mtv_lesson.validate(lesson), [])
        self.assertEqual(lesson["colors"], common.ROLE_COLORS)

    def test_schema_reject_five_distinct_errors(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        b = lesson["scenes"][0]["beats"][0]
        b["moves"].append("intro")
        b["patterns"].append("Flash")
        lesson["scenes"][0]["scene_kind"] = "2d"
        b["lands"].append({"mark": "nope", "visual": "x", "lead_s": 0.2})
        b["marks"]["reveal"] = 99
        errors = mtv_lesson.validate(lesson)
        self.assertEqual(len(set(errors)), 5)
        self.assertIn("s01-b01: moves value 'intro' not in MOVES", errors)
        self.assertIn("s01-b01: patterns value 'Flash' not a PATTERN_TAGS key", errors)
        self.assertIn("s01: scene_kind '2d' not in RUNTIME_SCENE_KINDS", errors)
        self.assertIn("s01-b01: lands mark 'nope' not in marks", errors)
        self.assertIn("s01-b01: marks['reveal'] = 99 past the word count 9", errors)

    def test_schema_reject_empty_narration(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        lesson["scenes"][0]["beats"][0]["narration"] = " ... "
        lesson["scenes"][0]["beats"][0]["marks"] = {}
        lesson["scenes"][0]["beats"][0]["lands"] = []
        self.assertIn("s01-b01: narration has no words", mtv_lesson.validate(lesson))

    def test_tail_defaults(self):
        path = Path(self.scratch.path) / "lesson.json"
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        for _, beat in mtv_lesson.beats(lesson):
            del beat["tail_s"]
        mtv_lesson.save(lesson, path)
        tails = [beat["tail_s"] for _, beat in mtv_lesson.beats(mtv_lesson.load(path))]
        self.assertEqual(tails, [0.4, 0.4, 1.0, 0.4, 0.4, 1.0])

    def test_beats_order_and_ids(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        self.assertEqual([b["id"] for _, b in mtv_lesson.beats(lesson)],
                         ["s01-b01", "s01-b02", "s01-b03", "s02-b01", "s02-b02", "s02-b03"])

    def test_early_stage_lesson_and_missing_fields(self):
        # Spec 6.6 validates the brief before any scene exists and the script before any
        # storyboard field does, so only schema, seed, the ids and narration are required.
        self.assertEqual(mtv_lesson.validate({"schema": "mtv-lesson/1", "seed": 1}), [])
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        for scene in lesson["scenes"]:
            for key in set(scene) - {"id", "title", "beats"}:
                del scene[key]
            for beat in scene["beats"]:
                for key in set(beat) - {"id", "narration"}:
                    del beat[key]
        self.assertEqual(mtv_lesson.validate(lesson), [])
        del lesson["seed"]
        del lesson["scenes"][1]["beats"][0]["narration"]
        del lesson["scenes"][1]["beats"][1]["id"]
        lesson["scenes"][1]["beats"][2]["marks"] = ["picture"]
        self.assertEqual(mtv_lesson.validate(lesson), [
            "missing field 'seed'",
            "s02-b01: missing field 'narration'",
            "scenes[1].beats[1]: missing field 'id'",
            "s02-b03: marks must be an object",
        ])


class TestLessonStages(unittest.TestCase):
    def test_stage_inputs_change_only_with_read_fields(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        before = mtv_lesson.stage_inputs(lesson, "narrate")
        lesson["scenes"][0]["beats"][0]["visual"] = "changed"
        self.assertEqual(mtv_lesson.stage_inputs(lesson, "narrate"), before)
        lesson["scenes"][0]["beats"][0]["narration"] = "Changed words."
        self.assertNotEqual(mtv_lesson.stage_inputs(lesson, "narrate"), before)

    def test_needs_rerun_and_mark_done(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        self.assertTrue(mtv_lesson.needs_rerun(lesson, "storyboard"))
        mtv_lesson.mark_done(lesson, "storyboard", {"python": "3.12.3"})
        self.assertFalse(mtv_lesson.needs_rerun(lesson, "storyboard"))
        self.assertEqual(lesson["stages"]["storyboard"]["tools"], {"python": "3.12.3"})
        self.assertRegex(lesson["stages"]["storyboard"]["done"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        lesson["scenes"][0]["beats"][0]["marks"]["reveal"] = 8
        self.assertTrue(mtv_lesson.needs_rerun(lesson, "storyboard"))

    def test_bump_counters(self):
        lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
        self.assertEqual(mtv_lesson.bump(lesson, "script_retries"), 1)
        self.assertEqual(mtv_lesson.bump(lesson, "render_retries", "s01"), 1)
        self.assertEqual(mtv_lesson.bump(lesson, "render_retries", "s01"), 2)
        self.assertEqual(lesson["attempts"]["render_retries"], {"s01": 2})

    def test_unknown_stage_raises(self):
        with self.assertRaises(KeyError):
            mtv_lesson.stage_inputs({}, "nope")


class TestTts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def test_interpolate_midpoints(self):
        self.assertAlmostEqual(tts.interpolate(4.0, 4, {"m": 1})["m"], 1.5)
        with self.assertRaises(ValueError):
            tts.interpolate(4.0, 0, {"m": 0})

    def test_alignment_numeral_expansion(self):
        require("num2words", "alignment")
        words = common.normalize_words("the 784 weights")
        tokens = [tts.Word("the", 0.0, 0.2), tts.Word("seven", 0.2, 0.5), tts.Word("hundred", 0.5, 0.8),
                  tts.Word("eighty-four", 0.8, 1.2), tts.Word("weights", 1.2, 1.6)]
        times, interpolated = tts.align_marks(words, tokens, {"n": 1, "w": len(words) - 1})
        self.assertFalse(interpolated)
        self.assertAlmostEqual(times["n"], 0.2)
        self.assertAlmostEqual(times["w"], 1.2)

    def test_alignment_falls_back_when_unmatched(self):
        self.assertEqual(tts.align_marks(["a", "b"], [], {"m": 0}), ({}, True))
        self.assertEqual(tts.align_marks(["a", "b"], [tts.Word("zzz", 0, 1)], {"m": 1}), ({}, True))

    def test_lcs_align_takes_earliest_matches(self):
        # Of two script words that could take the one spoken "the", the first does; a word
        # on one side only (the script's "x", the provider's "y") is skipped.
        self.assertEqual(tts.lcs_align(["the", "cat", "the"], ["the"]), {0: 0})
        self.assertEqual(tts.lcs_align(["a", "x", "b", "c"], ["a", "b", "y", "c"]), {0: 0, 2: 1, 3: 3})

    def test_null_provider_writes_wav(self):
        out = Path(self.scratch.path) / "b.wav"
        tokens = tts.get_provider("null").synthesize("Here is a network that already reads handwritten digits.", out)
        with wave.open(str(out)) as w:
            self.assertEqual((w.getframerate(), w.getnchannels(), w.getsampwidth()), (24000, 1, 2))
        self.assertAlmostEqual(tts.wav_duration(out), 9 * 0.4, places=2)
        self.assertEqual(len(tokens), 9)
        self.assertAlmostEqual(tokens[-1].end_s, 3.6, places=2)

    def test_words_from_characters(self):
        words = tts.words_from_characters(list("hi you"), [0, 0.1, 0.2, 0.3, 0.4, 0.5], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.assertEqual(words, [tts.Word("hi", 0, 0.2), tts.Word("you", 0.3, 0.6)])

    def test_unknown_provider(self):
        with self.assertRaises(ValueError):
            tts.get_provider("piper")


class TestKokoro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def setUp(self):
        require("kokoro", "kokoro")
        require("soundfile", "kokoro")

    def test_kokoro_chunks_join_with_offsets(self):
        # The pipeline's own chunking, stood in for so the case needs no weights: each
        # chunk's token times start at zero, and an untimed token (punctuation) is dropped.
        numpy = require("numpy", "kokoro")

        class Audio:
            def __init__(self, seconds):
                self.samples = numpy.zeros(round(seconds * 24000), dtype=numpy.float32)

            def numpy(self):
                return self.samples

        def token(text, start, end):
            return type("Token", (), {"text": text, "start_ts": start, "end_ts": end})

        def result(seconds, tokens):
            return type("Result", (), {"audio": Audio(seconds), "tokens": tokens})

        provider = tts.KokoroProvider()
        provider._pipeline = lambda text, voice, speed: iter([
            result(1.5, [token("one", 0.1, 0.6), token(".", None, None)]),
            result(1.0, [token("two", 0.2, 0.7)]),
        ])
        out = Path(self.scratch.path) / "chunks.wav"
        self.assertEqual(provider.synthesize("One. Two.", out),
                         [tts.Word("one", 0.1, 0.6), tts.Word("two", 1.7, 2.2)])
        self.assertAlmostEqual(tts.wav_duration(out), 2.5)

    def test_kokoro_tokens_and_784(self):
        out = Path(self.scratch.path) / "k.wav"
        try:
            tokens = tts.get_provider("kokoro").synthesize("There are 784 pixels.", out)
        except ConnectionError as exc:
            # The weights are a dependency like any module: unreachable, the case skips by name.
            _skip("kokoro", f"weights ({exc})")
        self.assertGreater(len(tokens), 0)
        self.assertTrue(all(t.start_s <= t.end_s for t in tokens))
        with wave.open(str(out)) as w:
            self.assertEqual(w.getframerate(), 24000)
        print("KOKORO 784 tokens:", [t.text for t in tokens])


class TestElevenLabs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def test_elevenlabs_words(self):
        require("elevenlabs", "elevenlabs")
        if not os.environ.get("ELEVENLABS_API_KEY"):
            print("SKIP elevenlabs: ELEVENLABS_API_KEY not available")
            raise unittest.SkipTest("no key")
        out = Path(self.scratch.path) / "e.wav"
        words = tts.get_provider("elevenlabs", voice=os.environ.get("MTV_TEST_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")).synthesize("Here is a network.", out)
        self.assertEqual(len(words), 4)
        self.assertAlmostEqual(tts.wav_duration(out), words[-1].end_s, delta=0.5)

    def test_elevenlabs_decodes_pcm_and_alignment(self):
        # The API's response shape, stood in for so the case needs no key: base64 16-bit
        # PCM at 24 kHz and the normalized character alignment.
        import base64
        require("elevenlabs", "elevenlabs")
        calls = []
        alignment = type("Alignment", (), {"characters": list("hi you"),
                                           "character_start_times_seconds": [0, 0.1, 0.2, 0.3, 0.4, 0.5],
                                           "character_end_times_seconds": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]})
        response = type("Response", (), {"audio_base_64": base64.b64encode(bytes(2 * 24000)).decode(),
                                         "normalized_alignment": alignment})

        class TextToSpeech:
            def convert_with_timestamps(self, **kwargs):
                calls.append(kwargs)
                return response

        provider = tts.ElevenLabsProvider("voice-id")
        provider._client = lambda: type("Client", (), {"text_to_speech": TextToSpeech()})
        out = Path(self.scratch.path) / "fake.wav"
        words = provider.synthesize("hi you", out, previous_text="before")
        self.assertEqual(words, [tts.Word("hi", 0, 0.2), tts.Word("you", 0.3, 0.6)])
        self.assertAlmostEqual(tts.wav_duration(out), 1.0)
        self.assertEqual(calls, [{"voice_id": "voice-id", "text": "hi you", "output_format": "pcm_24000",
                                  "previous_text": "before"}])

    def test_missing_key_is_not_retryable(self):
        env = {k: v for k, v in os.environ.items() if k != "ELEVENLABS_API_KEY"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                tts.get_provider("elevenlabs", voice="v").synthesize("hi", Path(self.scratch.path) / "k.wav")

    def test_neighbor_context_reaches_the_provider_only(self):
        beats = [{"narration": "one"}, {"narration": "two"}, {"narration": "three"}]
        self.assertEqual(narrate.neighbor_context(beats, 0), {"next_text": "two"})
        self.assertEqual(narrate.neighbor_context(beats, 1), {"previous_text": "one", "next_text": "three"})
        self.assertEqual(narrate.neighbor_context(beats, 2), {"previous_text": "two"})
        seen = []

        class Down:
            name = "down"
            def synthesize(self, text, out_wav, **context):
                seen.append(context)
                raise ConnectionError("down")
        _, used, _ = narrate.synthesize_with_retry(Down(), "hi there", Path(self.scratch.path) / "c.wav",
                                                   tts.get_provider("null"), sleep_fn=lambda s: None,
                                                   context={"previous_text": "one"})
        self.assertEqual((used, seen), ("null", [{"previous_text": "one"}] * 4))


class TestNarrate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def setUp(self):
        self.run_dir = example_run_dir(self.scratch.path)

    def test_narrate_null_provider(self):
        cp = run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        lesson = mtv_lesson.load(self.run_dir / "lesson.json")
        for _, beat in mtv_lesson.beats(lesson):
            self.assertTrue((self.run_dir / beat["audio"]).exists())
            self.assertTrue((self.run_dir / beat["words"]).exists())
            self.assertFalse(beat["interpolated"])
            for t in beat["marks_s"].values():
                self.assertTrue(0.0 <= t <= beat["duration_s"])
        self.assertIn("narrate", lesson["stages"])
        self.assertTrue(cp.stdout.strip().splitlines()[-1].startswith("PASS"))

    def test_narrate_cache_hit_and_deleted_wav(self):
        run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        wav = self.run_dir / "audio" / "s01-b01.wav"
        stamp = wav.stat().st_mtime_ns
        run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        self.assertEqual(wav.stat().st_mtime_ns, stamp)
        wav.unlink()
        cp = run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0)
        self.assertTrue(wav.exists())

    def test_retry_backoff_and_fallback(self):
        class Flaky:
            name = "flaky"
            def synthesize(self, text, out_wav):
                raise ConnectionError("down")
        sleeps = []
        tokens, used, retries = narrate.synthesize_with_retry(
            Flaky(), "hello there", Path(self.scratch.path) / "f.wav", tts.get_provider("null"), sleep_fn=sleeps.append)
        self.assertEqual(sleeps, [2.0, 4.0, 8.0])
        self.assertEqual((used, retries, len(tokens)), ("null", 3, 2))
        with self.assertRaises(ConnectionError):
            narrate.synthesize_with_retry(Flaky(), "hello there", Path(self.scratch.path) / "g.wav", None, sleep_fn=sleeps.append)
        self.assertIsNone(narrate.build_fallback("null"))
        self.assertIsNone(narrate.build_fallback("kokoro"))

    def test_elevenlabs_without_key_exits_2_before_any_beat(self):
        env = {k: v for k, v in os.environ.items() if k != "ELEVENLABS_API_KEY"}
        cp = run_script("narrate", "lesson.json", "--provider", "elevenlabs", cwd=self.run_dir, env=env)
        self.assertEqual(cp.returncode, 2)
        self.assertIn("ELEVENLABS_API_KEY", cp.stderr)
        self.assertFalse((self.run_dir / "audio").exists())

    def test_narrate_invalid_lesson_exits_2(self):
        lesson = mtv_lesson.load(self.run_dir / "lesson.json")
        lesson["scenes"][0]["scene_kind"] = "2d"
        mtv_lesson.save(lesson, self.run_dir / "lesson.json")
        self.assertEqual(run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir).returncode, 2)

    def test_warmup_needs_no_lesson(self):
        cp = run_script("narrate", "--warmup", "--provider", "null", cwd=self.scratch.path)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertRegex(cp.stdout.strip().splitlines()[-1], r"^PASS warmup null rtf=\d+\.\d{3}$")


class TestStoryboardCheck(ExampleLessonCase):
    def edit(self, fn):
        lesson = mtv_lesson.load(self.lesson_path)
        fn(lesson)
        mtv_lesson.save(lesson, self.lesson_path)

    def test_example_passes(self):
        cp = run_script("storyboard_check", "lesson.json", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout)
        self.assertTrue(mtv_lesson.load(self.lesson_path)["checks"]["storyboard"]["pass"])

    def test_unresolved_mark_and_symbol_before_value(self):
        def fn(lesson):
            lesson["scenes"][0]["beats"][0]["marks"]["reveal"] = 40
            lesson["scenes"][1]["beats"][0]["shows_value_of"] = []
        self.edit(fn)
        cp = run_script("storyboard_check", "lesson.json", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        findings = mtv_lesson.load(self.lesson_path)["checks"]["storyboard"]["findings"]
        self.assertIn(("s01-b01", None), [(f["beat"], f["rule_id"]) for f in findings])
        self.assertIn(("s02-b02", "R07"), [(f["beat"], f["rule_id"]) for f in findings])

    def test_script_r08_r09(self):
        def fn(lesson):
            for _, beat in mtv_lesson.beats(lesson):
                beat["narration"] = beat["narration"].replace("?", ".")
            lesson["scenes"][0]["beats"][0]["narration"] = " ".join(["word"] * 61) + "."
            lesson["scenes"][0]["beats"][0]["marks"] = {"reveal": 7}
        self.edit(fn)
        cp = run_script("storyboard_check", "lesson.json", "--script", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        rules = {f["rule_id"] for f in mtv_lesson.load(self.lesson_path)["checks"]["storyboard"]["findings"]}
        self.assertTrue({"R08", "R09"} <= rules)

    def test_exemplar_id_in_field(self):
        self.edit(lambda l: l["scenes"][0]["beats"][0].__setitem__("visual", "copy aircAruvnKk-s09-b03 staging"))
        cp = run_script("storyboard_check", "lesson.json", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("aircAruvnKk-s09-b03", cp.stdout)

    def test_unknown_lands_mark_is_a_finding(self):
        # validate reports it as well, yet an unresolved mark fails this gate, not the input.
        self.edit(lambda lesson: lesson["scenes"][1]["beats"][2]["lands"][0].__setitem__("mark", "gone"))
        cp = run_script("storyboard_check", "lesson.json", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1, cp.stderr)
        self.assertIn("s02-b03 - mark 'gone' does not resolve to a word", cp.stdout.splitlines())

    def test_other_schema_error_exits_2_without_writing(self):
        self.edit(lambda lesson: lesson["scenes"][0].__setitem__("scene_kind", "2d"))
        before = self.lesson_path.read_text()
        cp = run_script("storyboard_check", "lesson.json", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 2)
        self.assertIn("scene_kind '2d'", cp.stderr)
        self.assertEqual(self.lesson_path.read_text(), before)

    def test_predicate_keys(self):
        self.assertEqual(set(storyboard_check.PREDICATES), {"R01", "R03", "R06", "R07", "R08", "R09", "R10", "R11", "R16", "R28"})

    def test_predicates_match_framework(self):
        ref = SKILL_DIR / "references" / "framework.md"
        if not ref.exists():
            print("SKIP storyboard predicates: references/framework.md not present (M2 writes it)")
            raise unittest.SkipTest("references absent")
        blocks = [b for b in re.split(r"\n[ \t]*\n", ref.read_text()) if re.match(r"^R\d\d ", b)]
        self.assertEqual(len(blocks), 30)
        named = {b[:3] for b in blocks if "Check (storyboard): storyboard_check.py" in b}
        self.assertEqual(named, set(storyboard_check.PREDICATES))


class TestCheckScenes(ExampleLessonCase):
    def setUp(self):
        super().setUp()
        self.bin_dir = self.run_dir.parent / "bin"
        write_fake_manim(self.bin_dir)
        self.env = env_with_fake_manim(self.bin_dir)

    def test_every_banned_name_once(self):
        lines = [f"x{i} = {name}" for i, name in enumerate(sorted(common.BANNED_NAMES))]
        lines += ["self.frame.scale(2)", "self.play(mob.shift, UP)", "c = TEAL",
                  "class S01WorkingThing(Narrated3DScene):\n    pass",
                  "class S02OneNeuron(NarratedScene):\n    def construct(self):\n        zoom_to(self, m)\n        orbit_with_hud(self, h)"]
        source = "\n".join(lines) + "\n"
        findings = check_scenes.lint_source(source, mtv_lesson.load(self.lesson_path))
        names = [f["name"] for f in findings]
        for name in common.BANNED_NAMES:
            self.assertEqual(names.count(name), 1, name)
        for name in ("self.frame", "play(mob.method)", "TEAL", "S01WorkingThing", "zoom_to+orbit_with_hud"):
            self.assertIn(name, names)
        self.assertEqual(len({f["line"] for f in findings if f["name"] in common.BANNED_NAMES}), len(common.BANNED_NAMES))

    def test_cli_exit_1_one_finding_per_line_and_no_dry_run(self):
        (self.run_dir / "lesson.py").write_text("from manim import *\nfrom mtv.narrated import NarratedScene\nx = ShowCreation\n")
        cp = run_script("check_scenes", "lesson.py", "lesson.json", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 1)
        checks = mtv_lesson.load(self.lesson_path)["checks"]["scenes"]
        self.assertEqual(checks["dry_run"], {})
        self.assertEqual([f["line"] for f in checks["findings"] if f["name"] == "ShowCreation"], [3])

    def test_clean_file_runs_dry_run_per_class(self):
        (self.run_dir / "lesson.py").write_text(CLEAN_TWO_CLASS_SOURCE)
        cp = run_script("check_scenes", "lesson.py", "lesson.json", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(mtv_lesson.load(self.lesson_path)["checks"]["scenes"]["dry_run"],
                         {"S01WorkingThing": True, "S02OneNeuron": True})
        calls = [json.loads(l) for l in (self.bin_dir / "calls.jsonl").read_text().splitlines()]
        self.assertTrue(all("--dry_run" in c for c in calls))

    def test_missing_manim_exits_2(self):
        (self.run_dir / "lesson.py").write_text(CLEAN_TWO_CLASS_SOURCE)
        env = {**os.environ, "PATH": str(self.scratch.path)}
        self.assertEqual(run_script("check_scenes", "lesson.py", "lesson.json", cwd=self.run_dir, env=env).returncode, 2)

    def test_findings_decide_when_manim_is_missing(self):
        # A finding fails the gate whatever the environment, so it outranks the missing manim.
        (self.run_dir / "lesson.py").write_text(CLEAN_TWO_CLASS_SOURCE + "x = ShowCreation\n")
        env = {**os.environ, "PATH": str(self.scratch.path)}
        self.assertEqual(run_script("check_scenes", "lesson.py", "lesson.json", cwd=self.run_dir, env=env).returncode, 1)

    def test_failed_dry_run_exits_1_with_its_output(self):
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"][0]["scene_class"] = "S01BadThing"
        mtv_lesson.save(lesson, self.lesson_path)
        (self.run_dir / "lesson.py").write_text(CLEAN_TWO_CLASS_SOURCE.replace("S01WorkingThing", "S01BadThing"))
        cp = run_script("check_scenes", "lesson.py", "lesson.json", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        checks = mtv_lesson.load(self.lesson_path)["checks"]["scenes"]
        self.assertEqual(checks["dry_run"], {"S01BadThing": False, "S02OneNeuron": True})
        self.assertFalse(checks["pass"])
        self.assertIn("ValueError: S01BadThing failed its dry run", cp.stdout)

    def test_lint_reads_the_syntax_tree(self):
        # Words in comments and docstrings are not code, and an import names a module.
        self.assertEqual(check_scenes.banned_findings('"""Never open a file."""\n# no ImageMobject here\n'), [])
        imports = check_scenes.banned_findings("import manimlib\nfrom urllib.request import urlopen\n")
        self.assertEqual([(f["line"], f["name"]) for f in imports], [(1, "manimlib"), (2, "urllib")])
        broken = check_scenes.banned_findings("x = 1\ndef f(:\n")
        self.assertEqual([(f["line"], f["name"]) for f in broken], [(2, "syntax error")])
        missing = check_scenes.lint_source(CLEAN_TWO_CLASS_SOURCE.replace("S02OneNeuron", "S02Other"),
                                           mtv_lesson.load(self.lesson_path))
        self.assertEqual([(f["name"], f["fix"]) for f in missing], [("S02OneNeuron", "define class S02OneNeuron")])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the self-test; arguments not listed here (for example -k NAME) go to unittest.",
        allow_abbrev=False,
    )
    parser.add_argument("--patterns", action="store_true", help="render one example per patterns.py helper")
    parser.add_argument("--one-beat", action="store_true", help="render, assemble and verify a one-beat lesson")
    parser.add_argument("--fixtures", type=Path, metavar="DIR", help="write the fixture lessons into DIR")
    args, unittest_args = parser.parse_known_args()
    for flag, given in (
        ("--patterns", args.patterns),
        ("--one-beat", args.one_beat),
        ("--fixtures", args.fixtures is not None),
    ):
        if given:
            return common.usage_error(f"{flag} not implemented yet")
    program = unittest.main(argv=[sys.argv[0], *unittest_args], exit=False)
    return 0 if program.result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
