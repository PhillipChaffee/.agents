"""Standard-library self-test for the manim-teaching-video scripts.

Optional dependencies and tools are looked up inside the case that needs them, so a
machine without them still runs every other case and exits 0.
"""

from __future__ import annotations

import argparse
import configparser
import importlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
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

import mtv.common as common  # noqa: E402


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
