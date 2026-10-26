"""Standard-library self-test for the manim-teaching-video scripts.

Optional dependencies and tools are looked up inside the case that needs them, so a
machine without them still runs every other case and exits 0.
"""

from __future__ import annotations

import argparse
import base64
import configparser
import importlib
import json
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import NoReturn
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets"

# The self-test writes only to its scratch directories, so neither it nor a script
# that run_script starts may leave bytecode caches in the skill's scripts/ tree.
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS_DIR))

import assemble  # noqa: E402
import check_scenes  # noqa: E402
import exemplars  # noqa: E402
import frames  # noqa: E402
import mtv.common as common  # noqa: E402
import mtv.lesson as mtv_lesson  # noqa: E402
import mtv.narrated as narrated  # noqa: E402
import mtv.tts as tts  # noqa: E402
import narrate  # noqa: E402
import render  # noqa: E402
import storyboard_check  # noqa: E402
import verify  # noqa: E402


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
# the failing path with a scenes file that is otherwise clean. Its render writes what CE's
# --save_sections writes ({media_dir}/videos/{module}/{quality}/sections/<Class>.json and one
# MP4 per section) plus the mixin's run log, timing each beat at its duration_s + tail_s;
# MTV_FAKE_FAIL, MTV_FAKE_HANG and MTV_FAKE_FFMPEG select a failure, a hang, or real MP4s;
# MTV_FAKE_RUN_LOG=none or nobeat drops each run-log line or its beat key after a clean exit.
FAKE_MANIM_SOURCE = r'''"""A stand-in for ManimCE's manim command that records each call in calls.jsonl beside it."""
import ast
import json
import os
import subprocess
import sys
import time
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
lesson_py, scene_class = Path(argv[-2]), argv[-1]
# Like CE, the class is looked up in the scenes file; lesson.json supplies only its beats.
if scene_class not in {node.name for node in ast.parse(lesson_py.read_text()).body if isinstance(node, ast.ClassDef)}:
    sys.exit("There are no scenes inside that module")
if os.environ.get("MTV_FAKE_FAIL") == "1":
    sys.exit("TypeError: Passing Mobject methods to Scene.play is no longer supported. Use Mobject.animate instead.")
if os.environ.get("MTV_FAKE_HANG") == "1" and "--disable_caching" not in argv:
    time.sleep(30)
lesson = json.loads(Path(os.environ["MTV_LESSON"]).read_text())
beats = next(scene for scene in lesson["scenes"] if scene["scene_class"] == scene_class)["beats"]
sections_dir = Path(argv[argv.index("--media_dir") + 1]) / "videos" / lesson_py.stem / "480p15" / "sections"
sections_dir.mkdir(parents=True, exist_ok=True)
entries, enter_s = [], 0.0
with open(os.environ["MTV_RUN_LOG"], "a", encoding="utf-8") as run_log:
    for index, beat in enumerate(beats):
        audio_s = 2.0 if beat["duration_s"] is None else beat["duration_s"]
        tail_s = beat.get("tail_s") or 0.0
        duration = audio_s + tail_s
        video = f"{scene_class}_{index:04d}_{beat['id']}.mp4"
        if os.environ.get("MTV_FAKE_FFMPEG") == "1":
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                            f"color=c=blue:s=854x480:r=15:d={duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            str(sections_dir / video)], check=True)
        else:
            (sections_dir / video).touch()
        # CE writes nb_frames and duration as strings (manim/utils/commands.py:62-63).
        entries.append({"name": beat["id"], "type": "default.normal", "video": video, "width": 854, "height": 480,
                        "nb_frames": str(round(duration * 15)), "duration": f"{duration:.6f}",
                        "avg_frame_rate": "15/1", "codec_name": "h264", "pix_fmt": "yuv420p"})
        record = {"beat": beat["id"], "enter_s": enter_s, "exit_s": enter_s + duration,
                  "audio_s": audio_s, "tail_s": tail_s, "overrun_s": 0.0, "boxes": []}
        if os.environ.get("MTV_FAKE_RUN_LOG") == "nobeat":
            del record["beat"]
        if os.environ.get("MTV_FAKE_RUN_LOG") != "none":
            run_log.write(json.dumps(record) + "\n")
        enter_s += duration
(sections_dir / f"{scene_class}.json").write_text(json.dumps(entries, indent=4))
print("File ready")
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


# A 1x1 JPEG that Pillow wrote (Image.new("RGB", (1, 1)).save(buf, "JPEG")), so a synthetic
# pack's contact sheets need no Pillow at test time.
TINY_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAx"
    "NDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy"
    "MjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUF"
    "BAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVW"
    "V1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi"
    "4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAEC"
    "AxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVm"
    "Z2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq"
    "8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooooA//2Q=="
)

# (tag, exemplar id, confidence) of every entry in a clean synthetic pack.
PACK_ENTRIES = (
    ("numbers-before-symbols", "aaaaaaaaaaa-s01-b01", 0.9),
    ("numbers-before-symbols", "bbbbbbbbbbb-s02-b01", 0.85),
    ("working-thing-first", "ccccccccccc-s01-b01", 0.8),
    ("provenance-transform", "ddddddddddd-s01-b01", 0.7),
    ("viewer-voice", "orig-fixture-lesson-s01-b01", 1.0),
    ("one-then-all", "eeeeeeeeeee-s01-b01", 0.6),
)


def make_pack(pack_dir: Path, broken: bool) -> None:
    """A synthetic exemplar pack in the layout M2 builds: index.json, and one sheet and one
    excerpt per entry under its tag. ``broken`` adds exactly three check findings: an entry
    under an unknown tag, a deleted sheet and a tiles count of 7."""
    rows = PACK_ENTRIES + ((("made-up-tag", "fffffffffff-s01-b01", 0.5),) if broken else ())
    tags: dict[str, list[dict]] = {}
    for tag, exemplar_id, confidence in rows:
        entry = {
            "id": exemplar_id,
            "tiles": 4,
            "sheet": f"{tag}/{exemplar_id}.jpg",
            "excerpt": f"{tag}/{exemplar_id}.md",
            "rule_ids": ["R07"],
            "gist": "fixture gist",
            "confidence": confidence,
        }
        if exemplar_id.startswith("orig-"):
            entry.update(source="original", lesson_slug="fixture-lesson", scene_id="s01", beat_id="s01-b01",
                         helpers=["NumericColumn"], report="report.md")
        else:
            video_id, section_id, beat_id = exemplar_id.rsplit("-", 2)
            entry.update(source="corpus", video_id=video_id, section_id=section_id, beat_id=beat_id,
                         t_start=0.0, t_end=10.0)
        (pack_dir / tag).mkdir(parents=True, exist_ok=True)
        (pack_dir / entry["sheet"]).write_bytes(base64.b64decode(TINY_JPEG_B64))
        (pack_dir / entry["excerpt"]).write_text(f"# {exemplar_id}\nfixture excerpt\n", encoding="utf-8")
        tags.setdefault(tag, []).append(entry)
    if broken:
        (pack_dir / tags["numbers-before-symbols"][1]["sheet"]).unlink()
        tags["one-then-all"][0]["tiles"] = 7
    index = {
        "schema": "mtv-exemplars/1",
        "corpus_commit": "0123abcd",
        "built": "2026-11-20T10:00:00Z",
        "license_note": "local use only: contains frames and transcript excerpts from 3Blue1Brown videos; never redistribute",
        "tags": tags,
    }
    common.dump_json(index, pack_dir / "index.json")


def make_clip(path: Path, color: str, duration_s: float, fps: int = 15, size: str = "854x480") -> None:
    common.run_cmd([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={size}:r={fps}:d={duration_s}",
        "-pix_fmt", "yuv420p", str(path),
    ]).check_returncode()


def make_tone(path: Path, duration_s: float, rate: int = 24000) -> None:
    common.run_cmd([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_s}",
        "-ar", str(rate), "-ac", "1", str(path),
    ]).check_returncode()


def make_av(path: Path, video_src: str, tone_s: float = 12, shortest: bool = True) -> None:
    """An MP4 of the lavfi source ``video_src`` over a 440 Hz tone, as a finished video would carry.

    Without ``shortest`` the tone plays on past the video's last frame, as it may in a video
    muxed without the skill.
    """
    common.run_cmd([
        "ffmpeg", "-y", "-f", "lavfi", "-i", video_src, "-f", "lavfi", "-i", f"sine=frequency=440:duration={tone_s}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", *(["-shortest"] if shortest else []), str(path),
    ]).check_returncode()


def make_rendered_lesson(run_dir: Path, colors: list[str], tone_s: float = 1.5) -> Path:
    """Write ``run_dir/lesson.json`` as render.py would leave it, with one two-beat scene per color.

    The example lesson's header and its env, attempts, checks and stages blocks are kept,
    so the result validates and later stages name their outputs after its slug and title.
    Every beat renders as a 2 s clip of its scene's color over a ``tone_s`` narration tone.
    """
    lesson = mtv_lesson.load(ASSETS_DIR / "lesson.example.json")
    lesson.update(tier="draft", provider="null", scenes=[])
    (run_dir / "audio").mkdir(parents=True, exist_ok=True)
    marks = {"scene": 5}
    for n, color in enumerate(colors, 1):
        scene_id, scene_class = f"s{n:02d}", f"S{n:02d}Fixture"
        out_dir = run_dir / "render" / "draft" / scene_id
        out_dir.mkdir(parents=True)
        (out_dir / "render.log").write_text("")
        scene = {
            "id": scene_id, "title": f"Fixture scene {n}", "scene_class": scene_class, "scene_kind": "flat",
            "opening_state": "black" if n == 1 else "continue", "closing_state": "held", "beats": [],
        }
        sections = []
        for index, ordinal in enumerate(("one", "two")):
            beat_id = f"{scene_id}-b{index + 1:02d}"
            video = f"{scene_class}_{index:04d}_{beat_id}.mp4"
            make_clip(out_dir / video, color, 2.0)
            make_tone(run_dir / "audio" / f"{beat_id}.wav", tone_s)
            sections.append({
                "name": beat_id, "type": "default.normal", "video": video, "width": 854, "height": 480,
                "nb_frames": "30", "duration": "2.000000", "avg_frame_rate": "15/1", "codec_name": "h264",
                "pix_fmt": "yuv420p",
            })
            scene["beats"].append({
                "id": beat_id, "narration": f"This is beat {ordinal} of scene {scene_id}.", "marks": marks,
                "visual": f"a full-frame {color} field", "patterns": [],
                "moves": ["hook"] if n == 1 and index == 0 else ["concrete"],
                "introduces": [], "shows_value_of": [], "symbol_introduced": [], "lands": [], "tail_s": 0.5,
                "audio": f"audio/{beat_id}.wav", "duration_s": tone_s, "words": None,
                "marks_s": tts.interpolate(tone_s, 7, marks), "interpolated": False,
                "render": {
                    "index": index, "video": f"render/draft/{scene_id}/{video}", "duration_s": 2.0, "frames": [],
                    "log": {"enter_s": 2.0 * index, "exit_s": 2.0 * (index + 1), "audio_s": tone_s, "tail_s": 0.5,
                            "overrun_s": 0.0, "boxes": []},
                },
            })
        common.dump_json(sections, out_dir / "sections.json")
        lesson["scenes"].append(scene)
    classes = "".join(
        f"\n\nclass {scene['scene_class']}(NarratedScene):\n    def construct(self):\n        pass\n"
        for scene in lesson["scenes"]
    )
    (run_dir / "lesson.py").write_text("from manim import *\nfrom mtv.narrated import NarratedScene\n" + classes)
    lesson_path = run_dir / "lesson.json"
    mtv_lesson.save(lesson, lesson_path)
    return lesson_path


def shift_run_log(lesson_path: Path, seconds: float) -> None:
    """Move every beat's run-log entry and exit by ``seconds``, as a render whose clock drifted would."""
    lesson = mtv_lesson.load(lesson_path)
    for _, beat in mtv_lesson.beats(lesson):
        log = beat["render"]["log"]
        log["enter_s"] += seconds
        log["exit_s"] += seconds
    mtv_lesson.save(lesson, lesson_path)


# The example lesson's s01 as ManimCE 0.22.0 left it after a draft render through render.py: the
# section index byte for byte, and each beat's run-log line without its boxes. PyAV measured
# s01-b02 from its stream time base, 0.3 ms off its 143 frames, and the mixin's clock is a running
# sum of 1/15 s steps, so s01-b01 ends 5e-15 s past its target and logs that as its overrun.
MANIMCE_S01_SECTIONS = """[
    {
        "name": "s01-b01",
        "type": "default.normal",
        "video": "S01WorkingThing_0000_s01-b01.mp4",
        "width": 854,
        "height": 480,
        "nb_frames": "61",
        "duration": "4.066667",
        "avg_frame_rate": "15/1",
        "codec_name": "h264",
        "pix_fmt": "yuv420p"
    },
    {
        "name": "s01-b02",
        "type": "default.normal",
        "video": "S01WorkingThing_0001_s01-b02.mp4",
        "width": 854,
        "height": 480,
        "nb_frames": "143",
        "duration": "9.533008",
        "avg_frame_rate": "732160/48809",
        "codec_name": "h264",
        "pix_fmt": "yuv420p"
    },
    {
        "name": "s01-b03",
        "type": "default.normal",
        "video": "S01WorkingThing_0002_s01-b03.mp4",
        "width": 854,
        "height": 480,
        "nb_frames": "117",
        "duration": "7.800000",
        "avg_frame_rate": "15/1",
        "codec_name": "h264",
        "pix_fmt": "yuv420p"
    }
]"""
MANIMCE_S01_RUN_LOG = (
    {"enter_s": 0.0, "exit_s": 4.066666666666672, "audio_s": 3.6, "tail_s": 0.4, "overrun_s": 5.329070518200751e-15},
    {"enter_s": 4.066666666666672, "exit_s": 13.599999999999987, "audio_s": 9.2, "tail_s": 0.4, "overrun_s": 0.0},
    {"enter_s": 13.599999999999987, "exit_s": 21.39999999999998, "audio_s": 6.8, "tail_s": 1.0, "overrun_s": 0.0},
)


class ScratchCase(unittest.TestCase):
    """Gives each test its own empty work directory under one class scratch."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def setUp(self):
        self.work_dir = Path(tempfile.mkdtemp(dir=self.scratch.path))


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

    def test_scenes_file_edit_reruns_render_stages(self):
        # The fix loop (spec 6.6 step 8) edits only the generated lesson.py, so a resume must see
        # that edit in the render stages' hash, though the digest never reaches lesson.json.
        self.assertIsNone(mtv_lesson.load(ASSETS_DIR / "lesson.example.json")[mtv_lesson.SCENES_FILE_SHA256])
        scratch = Scratch()
        self.addCleanup(scratch.cleanup)
        lesson_path = example_run_dir(scratch.path) / "lesson.json"
        scenes_py = lesson_path.parent / "lesson.py"
        scenes_py.write_text(CLEAN_TWO_CLASS_SOURCE)
        lesson = mtv_lesson.load(lesson_path)
        for stage in mtv_lesson.STAGES:
            mtv_lesson.mark_done(lesson, stage, {})
        mtv_lesson.save(lesson, lesson_path)
        self.assertNotIn(mtv_lesson.SCENES_FILE_SHA256, common.load_json(lesson_path))
        lesson = mtv_lesson.load(lesson_path)
        self.assertEqual([stage for stage in mtv_lesson.STAGES if mtv_lesson.needs_rerun(lesson, stage)], [])
        scenes_py.write_text(CLEAN_TWO_CLASS_SOURCE + "# fix pass\n")
        lesson = mtv_lesson.load(lesson_path)
        self.assertEqual([stage for stage in mtv_lesson.STAGES if mtv_lesson.needs_rerun(lesson, stage)],
                         ["render.draft", "frames", "render.standard", "assemble", "verify"])

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


class StubScene(narrated.NarratedMixin):
    """Stands in for a ManimCE scene: records the calls the mixin makes, and its wait and play
    advance a clock instead of rendering frames."""

    frame_rate = 15.0

    def __init__(self) -> None:
        self.time = 0.0
        self.mobjects: list = []
        self.calls: list = []

    def next_section(self, name: str) -> None:
        self.calls.append(("next_section", name))

    def add_subcaption(self, text: str, duration: float) -> None:
        self.calls.append(("add_subcaption", text, duration))

    def wait(self, seconds: float) -> None:
        self.calls.append(("wait", seconds))
        self.time += seconds

    def play(self, seconds: float) -> None:
        self.time += seconds


class StubMobject:
    """Has CE's corner rule over its own points (CE manim/mobject/mobject.py:2395-2420) and no family."""

    def __init__(self, *points: tuple[float, float, float]) -> None:
        self.points = list(points)

    def get_all_points(self) -> list:
        return self.points

    def get_corner(self, direction) -> list[float]:
        return [(min if direction[d] < 0 else max)(p[d] for p in self.points) for d in range(3)]


class CairoClock:
    """CE's Cairo clock and section index, standing behind the mixin as ManimCE's Scene does.

    A segment rendered afresh writes whole frames: a play's count rounds up and each frame
    advances the clock (CE manim/scene/scene.py:1128-1129), a static wait's count rounds down
    and advances it in one step (CE manim/renderer/cairo_renderer.py:210,221-225). A segment
    found in ``cache`` is reused with the frames it was rendered with, while the clock advances
    by the exact run time and skip_animations stays set (cairo_renderer.py:104-110). A scene
    replaying the same calls hashes them the same, so a shared cache makes every play of a
    second render a hit.
    """

    frame_rate = 15.0

    def __init__(self, cache: set | None = None) -> None:
        self.renderer = SimpleNamespace(time=0.0, skip_animations=False)
        self.mobjects: list = []
        self.cache = set() if cache is None else cache
        # CE opens every scene with an autocreated section (scene_file_writer.py:264).
        self.sections: list[list] = [["autocreated", 0]]
        self.duration = 0.0
        self.frozen = False
        self.plays = self.hits = 0

    @property
    def time(self) -> float:
        return self.renderer.time

    def next_section(self, name: str) -> None:
        self.sections.append([name, 0])

    def add_subcaption(self, text: str, duration: float) -> None:
        pass

    def is_current_animation_frozen_frame(self) -> bool:
        return self.frozen

    def wait(self, seconds: float) -> None:
        self.play(seconds, frozen=True)

    def play(self, seconds: float, frozen: bool = False) -> None:
        dt = 1 / self.frame_rate
        self.duration, self.frozen = max(seconds, dt), frozen
        frames = int(self.duration / dt) if frozen else math.ceil(self.duration / dt)
        self.sections[-1][1] += frames
        key = (self.plays, self.duration, frozen)
        self.plays += 1
        self.renderer.skip_animations = key in self.cache
        if self.renderer.skip_animations:
            self.hits += 1
            self.renderer.time += self.duration
            return
        self.cache.add(key)
        if frozen:
            self.renderer.time += frames * dt
        else:
            for _ in range(frames):
                self.renderer.time += dt

    def index_spans(self) -> dict[str, tuple[float, float]]:
        """Each section's start and end as ruling F32 reads the index: a running sum in file order."""
        spans, start = {}, 0.0
        for name, frames in self.sections:
            spans[name] = (start, start + frames / self.frame_rate)
            start = spans[name][1]
        return spans


class FrameClockScene(narrated.NarratedMixin, CairoClock):
    """The mixin on CE's clock, as a generated scene subclasses it."""


class TestNarratedMixin(ExampleLessonCase):
    def setUp(self):
        super().setUp()
        cp = run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        run_log = str(self.run_dir / "run.log")
        # StubScene stands in for a scene, so the no-manim path is taken even where ManimCE is
        # installed: there config.frame_rate comes from whatever manim.cfg is in the working
        # directory, and look.apply would change the global config.
        for patcher in (mock.patch.dict(os.environ, {"MTV_LESSON": str(self.lesson_path), "MTV_RUN_LOG": run_log}),
                        mock.patch.object(narrated, "MANIM_AVAILABLE", False)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_until_and_remaining_clamp(self):
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with scene.beat("s01-b01") as b:
            reveal = b.marks_s["reveal"]
            self.assertAlmostEqual(b.until("reveal"), reveal - 0.2)
            self.assertAlmostEqual(b.until("reveal", lead=0.0), reveal)
            scene.wait(b.duration + 1.0)
            self.assertAlmostEqual(b.until("reveal"), 1 / 15)
            self.assertAlmostEqual(b.remaining(), 1 / 15)
        self.assertEqual(scene.calls[0], ("next_section", "s01-b01"))
        self.assertEqual(scene.calls[1][:2], ("add_subcaption", "Here is a network that already reads handwritten digits."))

    def test_exit_pads_to_target_end_and_cursor_accumulates(self):
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with scene.beat("s01-b01") as b:
            scene.wait(1.0)
        self.assertAlmostEqual(scene.time, b.duration + 0.4, places=6)
        with scene.beat("s01-b02") as b2:
            pass
        self.assertAlmostEqual(scene.time, b.duration + 0.4 + b2.duration + 0.4, places=6)

    def test_next_beat_takes_up_an_overrun(self):
        # Beat ends count from the scene start, so one beat's overrun does not push back the rest.
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with scene.beat("s01-b01") as b:
            scene.wait(b.duration + 0.4 + 0.5)
        with scene.beat("s01-b02") as b2:
            pass
        self.assertAlmostEqual(scene.time, b.duration + 0.4 + b2.duration + 0.4, places=6)

    def test_overrun_logged_and_line_shape(self):
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with scene.beat("s01-b01") as b:
            scene.wait(b.duration + 0.4 + 1.39)
        line = json.loads(Path(os.environ["MTV_RUN_LOG"]).read_text().splitlines()[-1])
        self.assertEqual(list(line), ["beat", "enter_s", "exit_s", "audio_s", "tail_s", "overrun_s", "boxes"])
        self.assertAlmostEqual(line["overrun_s"], 1.39, places=3)
        self.assertEqual(line["beat"], "s01-b01")
        self.assertAlmostEqual(line["audio_s"], b.duration)

    def test_load_lesson_requires_path_or_env(self):
        os.environ.pop("MTV_LESSON", None)
        with self.assertRaises(ValueError):
            StubScene().load_lesson("s01")

    def test_exception_inside_beat_is_neither_padded_nor_logged(self):
        # Spec 7.1: render.py surfaces the traceback of a beat missing from its logs.
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with self.assertRaises(ZeroDivisionError), scene.beat("s01-b01"):
            1 / 0
        self.assertEqual([call[0] for call in scene.calls], ["next_section", "add_subcaption"])
        self.assertFalse(Path(os.environ["MTV_RUN_LOG"]).exists())

    def test_boxes_cover_top_level_mobjects_with_points(self):
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        LayeredNetwork = type("LayeredNetwork", (StubMobject,), {})
        scene.mobjects = [LayeredNetwork((-5.1, 0.4, 0.0), (5.1, -3.2, 0.0)), StubMobject()]
        # DL and UR exist only where ManimCE imports; these are their values (CE manim/constants.py:151,154).
        with mock.patch.multiple(narrated, DL=(-1, -1, 0), UR=(1, 1, 0), create=True), scene.beat("s01-b01"):
            pass
        line = json.loads(Path(os.environ["MTV_RUN_LOG"]).read_text())
        self.assertEqual(line["boxes"], [{"name": "LayeredNetwork", "x0": -5.1, "y0": -3.2, "x1": 5.1, "y1": 0.4}])

    def test_run_log_times_chain_on_a_frame_clock(self):
        # The sync gate compares these times with CE's section index, which sums whole frames:
        # each beat enters where the last one left and ends within a frame of its narrated end.
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"][0]["beats"][0]["duration_s"] = 3.63  # off the frame grid, as synthesized audio is
        mtv_lesson.save(lesson, self.lesson_path)
        scene = FrameClockScene()
        scene.load_lesson("s01", self.lesson_path)
        for beat_id in ("s01-b01", "s01-b02", "s01-b03"):
            with scene.beat(beat_id):
                scene.play(0.5)  # 7.5 frames at 15 fps, so 8 frames
        lines = [json.loads(text) for text in Path(os.environ["MTV_RUN_LOG"]).read_text().splitlines()]
        self.assertEqual([line["beat"] for line in lines], ["s01-b01", "s01-b02", "s01-b03"])
        self.assertEqual(lines[0]["enter_s"], 0.0)
        target_end = 0.0
        for previous, line in zip([None, *lines], lines):
            if previous:
                self.assertEqual(line["enter_s"], previous["exit_s"])
            target_end += line["audio_s"] + line["tail_s"]
            self.assertLess(abs(line["exit_s"] - target_end), 1 / 15 + 1e-9)
        self.assertEqual(lines[-1]["exit_s"], scene.time)

    def test_cached_rerender_keeps_run_log_on_the_section_index(self):
        # A re-render reuses CE's cached segments, whose clock advances by exact run times while
        # the reused files hold whole frames; the run log must still match the index the sync gate
        # reads, and the pads must replay unchanged so every segment stays cached.
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"][0]["beats"][0]["duration_s"] = 3.63  # off the frame grid, as synthesized audio is
        mtv_lesson.save(lesson, self.lesson_path)
        run_log = Path(os.environ["MTV_RUN_LOG"])
        cache: set = set()
        renders = []
        for _ in range(2):
            run_log.unlink(missing_ok=True)
            scene = FrameClockScene(cache)
            scene.load_lesson("s01", self.lesson_path)
            for beat_id, mark in (("s01-b01", "reveal"), ("s01-b02", "lights"), ("s01-b03", "zoom")):
                with scene.beat(beat_id) as b:
                    for _ in range(3):
                        scene.play(0.5)  # 7.5 frames at 15 fps, so 8 frames
                    scene.wait(0.37)  # 5.55 frames, so 5 frames
                    scene.play(b.until(mark))
            lines = [json.loads(text) for text in run_log.read_text().splitlines()]
            spans = scene.index_spans()
            for line in lines:
                self.assertAlmostEqual(line["enter_s"], spans[line["beat"]][0], places=9)
                self.assertAlmostEqual(line["exit_s"], spans[line["beat"]][1], places=9)
            renders.append((lines, scene.hits, scene.plays))
        (first, first_hits, _), (second, second_hits, second_plays) = renders
        self.assertEqual(first_hits, 0)
        self.assertEqual(second_hits, second_plays)
        self.assertEqual(second, first)

    def test_no_run_log_without_mtv_run_log(self):
        # check_scenes.py's dry run leaves MTV_RUN_LOG unset: beats are still padded, nothing is written.
        os.environ.pop("MTV_RUN_LOG")
        scene = StubScene()
        scene.load_lesson("s01", self.lesson_path)
        with scene.beat("s01-b01"):
            pass
        self.assertEqual(scene.calls[-1][0], "wait")
        self.assertFalse((self.run_dir / "run.log").exists())

    def test_manim_path_takes_the_tier_frame_rate_and_applies_the_look(self):
        # Where ManimCE imports, the frame rate is the render tier's config value, not the scene's
        # attribute, and look.py styles the scene once per load.
        applied = []
        look = ModuleType("mtv.look")
        look.apply = applied.append
        scene = StubScene()
        with (mock.patch.object(narrated, "MANIM_AVAILABLE", True),
              mock.patch.object(narrated, "config", mock.Mock(frame_rate=30.0), create=True),
              mock.patch("mtv.look", look, create=True)):
            scene.load_lesson("s01", self.lesson_path)
            with scene.beat("s01-b01") as b:
                scene.wait(b.duration + 1.0)
                self.assertAlmostEqual(b.remaining(), 1 / 30)
        self.assertEqual(applied, [scene])


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


class TestRender(ExampleLessonCase):
    def setUp(self):
        super().setUp()
        cp = run_script("narrate", "lesson.json", "--provider", "null", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        (self.run_dir / "lesson.py").write_text(CLEAN_TWO_CLASS_SOURCE)
        self.bin_dir = self.run_dir.parent / "bin"
        write_fake_manim(self.bin_dir)
        self.env = env_with_fake_manim(self.bin_dir)

    def test_render_fills_render_and_env(self):
        cp = run_script("render", "lesson.json", "--tier", "draft", "--jobs", "2", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        lesson = mtv_lesson.load(self.lesson_path)
        for i, (scene, beat) in enumerate(mtv_lesson.beats(lesson)):
            self.assertEqual(beat["render"]["index"], i % 3)
            self.assertTrue((self.run_dir / beat["render"]["video"]).exists())
            self.assertAlmostEqual(beat["render"]["duration_s"], beat["duration_s"] + beat["tail_s"], places=2)
            self.assertEqual(set(beat["render"]["log"]), {"enter_s", "exit_s", "audio_s", "tail_s", "overrun_s", "boxes"})
        self.assertEqual(lesson["env"]["manim"], "Manim Community v0.22.0")
        self.assertEqual(lesson["env"]["python"], platform.python_version())
        self.assertTrue((self.run_dir / "render" / "draft" / "s01" / "sections.json").exists())
        self.assertIn("render.draft", lesson["stages"])

    def test_hang_is_killed_and_retried_with_disable_caching(self):
        env = {**self.env, "MTV_FAKE_HANG": "1"}
        cp = run_script("render", "lesson.json", "--tier", "draft", "--scenes", "s01", "--hang-timeout-s", "1",
                        cwd=self.run_dir, env=env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        calls = [json.loads(l) for l in (self.bin_dir / "calls.jsonl").read_text().splitlines()]
        self.assertEqual(["--disable_caching" in c for c in calls if "render" in c], [False, True])
        self.assertEqual(mtv_lesson.load(self.lesson_path)["attempts"]["render_retries"], {"s01": 1})

    def test_error_table_match_in_verdict(self):
        cp = run_script("render", "lesson.json", "--tier", "draft", "--scenes", "s01", cwd=self.run_dir,
                        env={**self.env, "MTV_FAKE_FAIL": "1"})
        self.assertEqual(cp.returncode, 1)
        self.assertIn(common.ERROR_TABLE[0].fix_text, cp.stdout.strip().splitlines()[-1])

    def test_missing_class_exits_1_without_traceback(self):
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"][0]["scene_class"] = "S01Missing"
        mtv_lesson.save(lesson, self.lesson_path)
        cp = run_script("render", "lesson.json", "--tier", "draft", "--scenes", "s01", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 1)
        self.assertNotIn("Traceback", cp.stderr)
        self.assertIn("There are no scenes inside that module", cp.stdout)  # the render.log tail, printed before the verdict
        self.assertIn(common.ERROR_TABLE[18].gl_idiom, cp.stdout.strip().splitlines()[-1])  # row 19 in the verdict

    def test_failed_rerender_leaves_no_stale_video(self):
        cp = run_script("render", "lesson.json", "--tier", "draft", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        before = mtv_lesson.load(self.lesson_path)
        # The fix loop edits lesson.py before it re-renders the scene (spec 6.6 step 8).
        scenes_py = self.run_dir / "lesson.py"
        scenes_py.write_text(scenes_py.read_text() + "# fix pass\n")
        cp = run_script("render", "lesson.json", "--tier", "draft", "--scenes", "s01", cwd=self.run_dir,
                        env={**self.env, "MTV_FAKE_FAIL": "1"})
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        after = mtv_lesson.load(self.lesson_path)
        # A failed render writes no render block and leaves the earlier stage, so s01's beats now
        # name videos that are gone, while s02, which was not re-rendered, keeps its own. The kept
        # stage no longer matches, because its hash covers lesson.py, so a resume renders again.
        self.assertEqual((after["stages"], after["scenes"]), (before["stages"], before["scenes"]))
        self.assertTrue(mtv_lesson.needs_rerun(after, "render.draft"))
        s01, s02 = (self.run_dir / "render" / "draft" / scene_id for scene_id in ("s01", "s02"))
        self.assertEqual(sorted(path.name for path in s01.iterdir() if path.is_file()), ["render.log", "run.log"])
        self.assertTrue((s02 / "sections.json").exists())
        for scene, beat in mtv_lesson.beats(after):
            self.assertEqual((self.run_dir / beat["render"]["video"]).exists(), scene["id"] == "s02")

    def test_failed_read_back_leaves_no_stale_video(self):
        # manim exits 0, so its MP4s are already copied when reading its run log fails; the copies
        # keep the earlier file names, so left in place they would pass for s01's earlier render.
        cp = run_script("render", "lesson.json", "--tier", "draft", cwd=self.run_dir, env=self.env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        before = mtv_lesson.load(self.lesson_path)
        s01 = self.run_dir / "render" / "draft" / "s01"
        for mode, reason in (("none", "missing from run.log"),
                             ("nobeat", "mtv: run.log line without a beat key")):
            with self.subTest(mode=mode):
                cp = run_script("render", "lesson.json", "--tier", "draft", "--scenes", "s01", cwd=self.run_dir,
                                env={**self.env, "MTV_FAKE_RUN_LOG": mode})
                self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
                self.assertNotIn("Traceback", cp.stderr)
                self.assertIn(reason, cp.stdout.strip().splitlines()[-1])
                after = mtv_lesson.load(self.lesson_path)
                self.assertEqual((after["stages"], after["scenes"]), (before["stages"], before["scenes"]))
                left = sorted(path.name for path in s01.iterdir() if path.is_file())
                self.assertEqual(left, ["render.log", "run.log"])
                self.assertFalse(render._rendered(after["scenes"][0], "draft", self.run_dir))

    def test_record_env_font_probe(self):
        # mtv.look arrives with Task 17 and imports manim, so a stub package stands in for it on
        # the probe's path; "" is pick_font's answer when no candidate is installed (Pango's default).
        for i, (body, font) in enumerate((('return "CMU Serif"', "CMU Serif"), ('return ""', ""),
                                          ('raise ImportError("manim")', None))):
            with self.subTest(font=font):
                scripts = self.run_dir.parent / f"stub-scripts-{i}"
                (scripts / "mtv").mkdir(parents=True)
                (scripts / "mtv" / "__init__.py").write_text("")
                (scripts / "mtv" / "look.py").write_text(f"def pick_font():\n    {body}\n")
                lesson = {}
                render.record_env(lesson, scripts)
                self.assertEqual(lesson["env"]["font"], font)
                self.assertEqual(lesson["env"]["pythonpath"].split(os.pathsep)[0], str(scripts))


class TestExemplars(ExampleLessonCase):
    def setUp(self):
        super().setUp()
        self.pack = self.run_dir.parent / "pack"

    def test_check_broken_pack_three_findings(self):
        make_pack(self.pack, broken=True)
        findings = exemplars.check(self.pack)
        self.assertEqual(len(findings), 3, findings)
        self.assertTrue(any("not in TECHNIQUE_TAGS" in f for f in findings))
        self.assertTrue(any("sheet" in f and "missing" in f for f in findings))
        self.assertTrue(any("tiles 7 outside 2 to 6" in f for f in findings))
        self.assertEqual(run_script("exemplars", "check", str(self.pack), cwd=self.run_dir).returncode, 1)

    def test_check_clean_pack_exit_0(self):
        make_pack(self.pack, broken=False)
        self.assertEqual(exemplars.check(self.pack), [])
        self.assertEqual(run_script("exemplars", "check", str(self.pack), cwd=self.run_dir).returncode, 0)

    def test_check_missing_dir_exit_1(self):
        cp = run_script("exemplars", "check", str(self.pack / "nope"), cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        self.assertIn("index.json missing", cp.stdout)
        self.assertNotIn("Traceback", cp.stderr)

    def test_pick_storyboarder_deterministic(self):
        make_pack(self.pack, broken=False)
        env = {**os.environ, "MTV_EXEMPLARS": str(self.pack)}
        first = run_script("exemplars", "pick", "--role", "storyboarder", "lesson.json", cwd=self.run_dir, env=env).stdout
        second = run_script("exemplars", "pick", "--role", "storyboarder", "lesson.json", cwd=self.run_dir, env=env).stdout
        self.assertEqual(first, second)
        ids = [p["id"] for p in json.loads(first)]
        self.assertEqual(ids[1], "aaaaaaaaaaa-s01-b01")  # numbers-before-symbols, confidence 0.9 beats 0.85
        self.assertEqual(mtv_lesson.load(self.lesson_path)["exemplars"]["used"]["storyboarder"], ids)
        self.assertTrue(len(ids) <= 8)

    def test_pick_frame_critic_reachable_tags(self):
        make_pack(self.pack, broken=False)
        env = {**os.environ, "MTV_EXEMPLARS": str(self.pack)}
        cp = run_script("exemplars", "pick", "--role", "frame-critic", "--scene", "s02", "lesson.json", cwd=self.run_dir, env=env)
        picks = json.loads(cp.stdout)
        self.assertTrue(1 <= len(picks) <= 4)
        scene = mtv_lesson.scene_by_id(mtv_lesson.load(self.lesson_path), "s02")
        reachable = set()
        for beat in scene["beats"]:
            for p in beat["patterns"]:
                reachable.update(common.PATTERN_TAGS[p])
            for m in beat["moves"]:
                reachable.add(common.MOVE_TAGS[m])
        self.assertTrue({p["tag"] for p in picks} <= reachable)

    def test_check_defaults_to_env_and_prints_index_sha256(self):
        # The brief stage copies the printed hash into exemplars.index_sha256.
        make_pack(self.pack, broken=False)
        cp = run_script("exemplars", "check", cwd=self.run_dir, env={**os.environ, "MTV_EXEMPLARS": str(self.pack)})
        sha = common.sha256_file(self.pack / "index.json")
        self.assertEqual(cp.stdout.splitlines(), [f"index.json sha256 {sha}", "PASS 6 exemplars under 5 tags"])
        unset = {name: value for name, value in os.environ.items() if name != "MTV_EXEMPLARS"}
        self.assertEqual(run_script("exemplars", "check", cwd=self.run_dir, env=unset).returncode, 2)

    def test_jpeg_size_and_oversized_sheet(self):
        make_pack(self.pack, broken=False)
        sheet = self.pack / "working-thing-first" / "ccccccccccc-s01-b01.jpg"
        self.assertEqual(exemplars.jpeg_size(sheet), (1, 1))
        data = sheet.read_bytes()
        sof = data.index(b"\xff\xc0")
        # A frame header holds its length and precision, then the height and the width.
        sheet.write_bytes(data[: sof + 5] + struct.pack(">HH", 481, 1281) + data[sof + 9 :])
        self.assertEqual(exemplars.jpeg_size(sheet), (1281, 481))
        self.assertEqual(exemplars.check(self.pack), ["ccccccccccc-s01-b01: sheet 1281x481 larger than 1280x480"])
        sheet.write_bytes(b"not a jpeg")
        with self.assertRaises(ValueError):
            exemplars.jpeg_size(sheet)
        self.assertEqual(exemplars.check(self.pack),
                         ["ccccccccccc-s01-b01: sheet 'working-thing-first/ccccccccccc-s01-b01.jpg' is not a JPEG"])

    def test_pick_budgets_and_camera_tag(self):
        make_pack(self.pack, broken=False)
        (self.pack / "viewer-voice" / "orig-fixture-lesson-s01-b01.md").write_text("# long\n" + "word " * 40)
        index = common.load_json(self.pack / "index.json")
        index["tags"]["camera-as-narrator"] = [dict(index["tags"]["working-thing-first"][0], id="ggggggggggg-s01-b01")]
        lesson = mtv_lesson.load(self.lesson_path)
        picks = exemplars.pick_storyboarder(index, lesson, self.pack, max_words=20)
        # Each fixture excerpt has 4 words and stays whole; the 42-word one gets what is left.
        self.assertEqual([(p["id"], p["words"]) for p in picks], [
            ("ccccccccccc-s01-b01", 4), ("aaaaaaaaaaa-s01-b01", 4),
            ("ddddddddddd-s01-b01", 4), ("orig-fixture-lesson-s01-b01", 8),
        ])
        lesson["scenes"][1]["scene_kind"] = "camera"
        self.assertEqual(exemplars.pick_storyboarder(index, lesson, self.pack)[-1]["id"], "ggggggggggg-s01-b01")
        self.assertEqual(len(exemplars.pick_storyboarder(index, lesson, self.pack, max_images=2)), 2)

    def test_pick_usage_errors_exit_2_without_writing(self):
        make_pack(self.pack, broken=True)
        env = {**os.environ, "MTV_EXEMPLARS": str(self.pack)}
        for args in (
            ("--role", "frame-critic"),
            ("--role", "frame-critic", "--scene", "s09"),
            ("--role", "storyboarder"),
        ):
            cp = run_script("exemplars", "pick", *args, "lesson.json", cwd=self.run_dir, env=env)
            self.assertEqual(cp.returncode, 2, args)
            self.assertEqual(cp.stdout, "", args)
        self.assertEqual(mtv_lesson.load(self.lesson_path)["exemplars"]["used"], {"storyboarder": [], "frame-critic": {}})


class TestFrames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = Scratch()
        cls.addClassCleanup(cls.scratch.cleanup)

    def setUp(self):
        self.run_dir = Path(tempfile.mkdtemp(dir=self.scratch.path))

    def test_continuity_jump_fails_at_threshold(self):
        require_tool("ffmpeg", "frames continuity")
        lesson_path = make_rendered_lesson(self.run_dir, ["blue", "blue", "white"])
        cp = run_script("frames", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        cont = common.load_json(self.run_dir / "frames" / "continuity.json")
        self.assertEqual(cont["threshold"], common.CONTINUITY_THRESHOLD)
        self.assertEqual([b["pass"] for b in cont["boundaries"]], [True, False])
        self.assertLess(cont["boundaries"][0]["mad"], common.CONTINUITY_THRESHOLD)
        # blue to white measures 0.886 here, so the jump still fails after the M1 calibration
        # raises the threshold to at most 0.30; blue to red (0.184) would not
        self.assertGreater(cont["boundaries"][1]["mad"], common.CONTINUITY_THRESHOLD)
        lesson = mtv_lesson.load(lesson_path)
        self.assertIn("frames/s01/s01-b02-last.png", lesson["scenes"][0]["beats"][1]["render"]["frames"])
        self.assertIn("frames/s02/s02-b01-first.png", lesson["scenes"][1]["beats"][0]["render"]["frames"])

    def test_mark_past_end_is_clamped(self):
        require_tool("ffmpeg", "frames clamp")
        lesson_path = make_rendered_lesson(self.run_dir, ["blue"])
        lesson = mtv_lesson.load(lesson_path)
        lesson["scenes"][0]["beats"][0]["marks_s"] = {"late": 2.4}
        mtv_lesson.save(lesson, lesson_path)
        cp = run_script("frames", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertTrue((self.run_dir / "frames" / "s01" / "s01-b01-late.png").exists())
        self.assertAlmostEqual(frames.clamp_time(2.4, 2.0, 15), 2.0 - 1 / 15)

    def test_unrendered_beat_exits_2_without_writing(self):
        require_tool("ffmpeg", "frames unrendered")
        lesson_path = self.run_dir / "lesson.json"
        shutil.copyfile(ASSETS_DIR / "lesson.example.json", lesson_path)
        before = lesson_path.read_text()
        cp = run_script("frames", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
        self.assertIn("s01-b01: no draft render.video", cp.stderr)
        self.assertEqual(lesson_path.read_text(), before)
        self.assertFalse((self.run_dir / "frames").exists())

    def test_sheet_requires_pil(self):
        require_tool("ffmpeg", "frames sheet")
        require("PIL", "frames sheet")
        clip = Path(self.scratch.path) / "c.mp4"
        make_clip(clip, "blue", 2.0)
        out = Path(self.scratch.path) / "sheet.jpg"
        self.assertTrue(frames.sheet(clip, 2.0, 0.0, out))
        from PIL import Image
        with Image.open(out) as image:
            self.assertEqual(image.size, (1278, 480))


class TestAssemble(ExampleLessonCase):
    """make_rendered_lesson replaces the example lesson in each test's run directory."""

    def test_assemble_two_streams_and_srt(self):
        require_tool("ffmpeg", "assemble")
        require_tool("ffprobe", "assemble")
        lesson_path = make_rendered_lesson(self.run_dir, ["blue", "red"], tone_s=1.5)
        cp = run_script("assemble", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        out = self.run_dir / "out" / "what-a-neuron-computes.draft.mp4"
        info = common.ffprobe_json(out)
        self.assertEqual(sorted(s["codec_type"] for s in info["streams"]), ["audio", "video"])
        self.assertAlmostEqual(float(info["format"]["duration"]), 8.0, delta=0.5)
        srt = (self.run_dir / "out" / "what-a-neuron-computes.srt").read_text()
        self.assertEqual(srt.count(" --> "), 4)
        self.assertIn("00:00:02,000 --> ", srt)
        self.assertEqual(mtv_lesson.load(lesson_path)["stages"]["assemble"]["tools"], {"saturation": "1.5"})
        verdict = cp.stdout.strip().splitlines()[-1]
        self.assertRegex(verdict, r"^PASS assembled out/what-a-neuron-computes\.draft\.mp4 \(\d+\.\d\d s\)$")

    def test_assemble_resamples_44100_wav(self):
        require_tool("ffmpeg", "assemble resample")
        require_tool("ffprobe", "assemble resample")
        lesson_path = make_rendered_lesson(self.run_dir, ["blue"], tone_s=1.5)
        make_tone(self.run_dir / "audio" / "s01-b01.wav", 1.5, rate=44100)
        cp = run_script("assemble", "lesson.json", "--tier", "draft", "--saturation", "1.0", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        with wave.open(str(self.run_dir / "out" / ".narration.draft.wav")) as narration:
            self.assertEqual((narration.getframerate(), narration.getnchannels()), (24000, 1))
        self.assertEqual(mtv_lesson.load(lesson_path)["stages"]["assemble"]["tools"], {"saturation": "1.0"})

    def test_srt_timestamp(self):
        self.assertEqual(assemble.srt_timestamp(3661.25), "01:01:01,250")

    def test_srt_cues_start_at_rendered_beat_offsets(self):
        # 1.2 s of narration and the 0.5 s tail end 0.3 s before each 2 s beat video, so only
        # offsets summed from render.duration_s start the second cue at 2 s.
        require_tool("ffmpeg", "assemble srt")
        require_tool("ffprobe", "assemble srt")
        make_rendered_lesson(self.run_dir, ["blue"], tone_s=1.2)
        cp = run_script("assemble", "lesson.json", "--tier", "draft", "--saturation", "1.0", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(
            (self.run_dir / "out" / "what-a-neuron-computes.srt").read_text(),
            "1\n00:00:00,000 --> 00:00:01,200\nThis is beat one of scene s01.\n\n"
            "2\n00:00:02,000 --> 00:00:03,200\nThis is beat two of scene s01.\n",
        )

    def test_missing_audio_or_tier_video_exits_2_without_writing(self):
        require_tool("ffmpeg", "assemble missing inputs")
        require_tool("ffprobe", "assemble missing inputs")
        lesson_path = make_rendered_lesson(self.run_dir, ["blue"], tone_s=1.5)
        (self.run_dir / "audio" / "s01-b02.wav").unlink()
        before = lesson_path.read_text()
        # The fixture renders the draft tier only, so no beat has a standard video.
        cp = run_script("assemble", "lesson.json", "--tier", "standard", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 2, cp.stdout + cp.stderr)
        self.assertIn("s01-b01: no standard render.video", cp.stderr)
        self.assertIn("s01-b02: no audio", cp.stderr)
        self.assertEqual(lesson_path.read_text(), before)
        self.assertFalse((self.run_dir / "out").exists())


class TestVerify(ExampleLessonCase):
    """Each test verifies a freshly rendered, reviewed and assembled two-scene lesson."""

    def setUp(self):
        super().setUp()
        require_tool("ffmpeg", "verify")
        require_tool("ffprobe", "verify")
        make_rendered_lesson(self.run_dir, ["blue", "blue"], tone_s=1.5)
        for script in ("frames", "assemble"):
            cp = run_script(script, "lesson.json", "--tier", "draft", cwd=self.run_dir)
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_verify_passes_then_shifted_log_fails_sync(self):
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        lesson = mtv_lesson.load(self.lesson_path)
        gates = {g["gate"]: g for g in lesson["checks"]["verify"]["gates"]}
        self.assertEqual(len(gates), 10)
        self.assertTrue(all(g["pass"] for g in gates.values()))
        self.assertEqual(gates["run log vs section index"]["tolerance"], common.SYNC_BEAT_TOLERANCE_S)
        self.assertEqual(gates["container duration"]["tolerance"], common.SYNC_CONTAINER_TOLERANCE_S)
        self.assertEqual(gates["banned names"]["measured"], 0)
        report = (self.run_dir / "report.md").read_text()
        self.assertTrue(report.startswith("# What a neuron computes\n"))
        self.assertIn("Hard gates:", report)
        shift_run_log(self.lesson_path, 0.5)
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        gates = {g["gate"]: g for g in mtv_lesson.load(self.lesson_path)["checks"]["verify"]["gates"]}
        self.assertFalse(gates["run log vs section index"]["pass"])
        # The failure drops the first run's verify stage, so neither a resume nor the report
        # takes the earlier pass for this verdict.
        lesson = mtv_lesson.load(self.lesson_path)
        self.assertNotIn("verify", lesson["stages"])
        self.assertTrue(mtv_lesson.needs_rerun(lesson, "verify"))
        resume = (self.run_dir / "report.md").read_text().splitlines()[-1]
        self.assertTrue(resume.startswith("Resume:"), resume)
        self.assertNotIn("verify", resume)

    def test_pass_at_another_tier_leaves_verify_stage_undone(self):
        # The verify stage's hash holds lesson.tier, not --tier, so a draft pass of a lesson
        # delivered at standard must not stand for the standard file's verify.
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        lesson = mtv_lesson.load(self.lesson_path)
        self.assertIn("verify", lesson["stages"])
        lesson["tier"] = "standard"
        mtv_lesson.save(lesson, self.lesson_path)
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        lesson = mtv_lesson.load(self.lesson_path)
        self.assertNotIn("verify", lesson["stages"])
        self.assertTrue(mtv_lesson.needs_rerun(lesson, "verify"))

    def test_report_with_every_warning_lints_clean(self):
        # Task 22 lints the run directory with the kit's markdownlint gate. Of the rules that
        # gate turns off, MD013 (line length) is the only one a report can trip, so only it is off.
        require_tool("markdownlint-cli2", "verify report lint")
        lesson = mtv_lesson.load(self.lesson_path)
        first, second = lesson["scenes"][0]["beats"]
        first["render"]["log"]["overrun_s"] = 1.2
        second["interpolated"] = True
        findings = ["index.json: corpus_commit missing", "sheet.png: not JPEG"]
        lesson["exemplars"].update(dir="pack", check_findings=findings)
        mtv_lesson.mark_done(lesson, "narrate", {"provider": "elevenlabs", "fallback": "kokoro"})
        lesson["env"]["font"] = ""
        scores = {"scores": {f"R{n:02d}": 2 for n in range(1, 17)}}
        lesson["checks"].update(
            storyboard={"pass": True},
            frames={"scenes": {"s01": scores, "s02": scores}, "final": {**scores, "zeros": []}},
        )
        mtv_lesson.save(lesson, self.lesson_path)
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        report = (self.run_dir / "report.md").read_text()
        for text in ("interpolated beats: s01-b02", "not JPEG", "provider fallback to kokoro", "overrun s01-b01"):
            self.assertIn(text, report)
        common.dump_json({"config": {"MD013": False}}, self.run_dir / ".markdownlint-cli2.jsonc")
        cp = common.run_cmd(["markdownlint-cli2", "report.md"], cwd=self.run_dir)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_wav_longer_than_beat_fails(self):
        make_tone(self.run_dir / "audio" / "s01-b01.wav", 2.6)
        cp = run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        self.assertEqual(cp.returncode, 1)
        gates = {g["gate"]: g for g in mtv_lesson.load(self.lesson_path)["checks"]["verify"]["gates"]}
        self.assertFalse(gates["wav within beat"]["pass"])

    def test_overrun_and_continuity_gates(self):
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"][0]["beats"][0]["render"]["log"]["overrun_s"] = 1.2
        mtv_lesson.save(lesson, self.lesson_path)
        (self.run_dir / "frames" / "continuity.json").unlink()
        run_script("verify", "lesson.json", "--tier", "draft", cwd=self.run_dir)
        gates = {g["gate"]: g for g in mtv_lesson.load(self.lesson_path)["checks"]["verify"]["gates"]}
        self.assertFalse(gates["overrun"]["pass"])
        self.assertEqual(gates["continuity"]["measured"], "missing")


class TestVerifyManimCEOutput(ExampleLessonCase):
    """The sync gates and the report read a section index and a run log that ManimCE wrote."""

    def test_manimce_index_and_clock_pass_until_shifted(self):
        lesson = mtv_lesson.load(self.lesson_path)
        lesson["scenes"] = lesson["scenes"][:1]
        out_dir = self.run_dir / "render" / "draft" / "s01"
        out_dir.mkdir(parents=True)
        (out_dir / "sections.json").write_text(MANIMCE_S01_SECTIONS)
        for beat, log in zip(lesson["scenes"][0]["beats"], MANIMCE_S01_RUN_LOG):
            beat["render"]["log"] = dict(log)
        mtv_lesson.save(lesson, self.lesson_path)
        sync = verify.run_log_vs_section_index(lesson, self.run_dir, "draft")[0]
        self.assertTrue(sync.passed)
        self.assertLess(sync.measured, 0.001)
        self.assertEqual(verify.index_coverage(lesson, self.run_dir, "draft")[0].measured, 0)
        # A beat that ended on time is no overrun, whatever float noise CE's clock leaves.
        self.assertEqual(verify._warnings(lesson), [])
        shift_run_log(self.lesson_path, 0.5)
        sync = verify.run_log_vs_section_index(mtv_lesson.load(self.lesson_path), self.run_dir, "draft")[0]
        self.assertFalse(sync.passed)


class TestVerifyExternal(ScratchCase):
    """verify.py --external judges an MP4 made without a lesson, a baseline run's included."""

    def test_black_frozen_good(self):
        require_tool("ffmpeg", "verify external")
        require_tool("ffprobe", "verify external")
        d = self.work_dir
        make_av(d / "black.mp4", "color=c=black:s=854x480:r=15:d=12")
        make_av(d / "frozen.mp4", "color=c=blue:s=854x480:r=15:d=12")
        make_av(d / "good.mp4", "testsrc=size=854x480:rate=15:duration=12")
        codes = [run_script("verify", "--external", str(d / name), cwd=d).returncode for name in ("black.mp4", "frozen.mp4", "good.mp4")]
        self.assertEqual(codes, [1, 1, 0])

    def test_rows_name_the_failing_gates_and_nothing_is_written(self):
        require_tool("ffmpeg", "verify external")
        require_tool("ffprobe", "verify external")
        d = self.work_dir
        # Too short for two samples ten seconds apart, so they sit a third and two thirds of the way in.
        make_av(d / "black.mp4", "color=c=black:s=854x480:r=15:d=4")
        make_av(d / "good.mp4", "testsrc=size=854x480:rate=15:duration=4")
        self.assertEqual({g.gate for g in verify.external(d / "black.mp4") if not g.passed}, {"not black", "not frozen"})
        self.assertTrue(all(g.passed for g in verify.external(d / "good.mp4")))
        absent = {g.gate: g for g in verify.external(d / "absent.mp4")}
        self.assertEqual(list(absent), ["exists", "streams", "container vs audio", "no manimlib beside", "not black", "not frozen"])
        self.assertEqual(absent["exists"].measured, verify.MISSING)
        self.assertFalse(any(g.passed for name, g in absent.items() if name != "no manimlib beside"))
        (d / "scene.py").write_text("from manimlib import *\n")
        before = sorted(d.iterdir())
        cp = run_script("verify", "--external", str(d / "good.mp4"), cwd=d)
        self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
        lines = cp.stdout.splitlines()
        self.assertEqual(len(lines), 7, cp.stdout)
        self.assertEqual(lines[-1], "FAIL verify --external: no manimlib beside")
        self.assertEqual(sorted(d.iterdir()), before)

    def test_samples_follow_the_video_stream(self):
        require_tool("ffmpeg", "verify external")
        require_tool("ffprobe", "verify external")
        d = self.work_dir
        # The tone runs 0.3 s past the last frame, inside the container gate's 0.5 s; samples
        # taken against the file's 20.3 s would seek to 20 s, after the video has ended.
        make_av(d / "long-tone.mp4", "testsrc=size=854x480:rate=15:duration=20", tone_s=20.3, shortest=False)
        gates = verify.external(d / "long-tone.mp4")
        self.assertTrue(all(g.passed for g in gates), [g.as_dict() for g in gates])
        # Never the first frame, which a lesson opening from black renders black; never past the
        # last frame's start, even when the stream's duration runs past it as PyAV's can.
        self.assertEqual(verify._sample_times(55.666667, 15), [10.0, 20.0, 30.0, 40.0, 50.0])
        self.assertLessEqual(verify._sample_times(30.0003, 15)[-1], 30.0003 - 1 / 15)
        reason = "ffmpeg read no frame at 10.000 s of long-tone.mp4: Output file is empty"
        with mock.patch.object(verify.frames, "gray_small", side_effect=RuntimeError(reason)):
            rows = {g.gate: g for g in verify.external(d / "long-tone.mp4")}
        for gate in ("not black", "not frozen"):
            self.assertEqual(rows[gate].measured, f"{verify.UNREADABLE}: {reason}")
            self.assertFalse(rows[gate].passed)


class TestPreflight(ScratchCase):
    def test_preflight_json_reports_install_lines(self):
        cp = run_script("preflight", "--json", "--provider", "null", cwd=self.work_dir)
        report = json.loads(cp.stdout)
        checks = {c["name"]: c for c in report["checks"]}
        self.assertEqual(list(checks), ["python", "manim", "latex", "dvisvgm", "ffmpeg", "ffprobe", "provider", "font", "disk", "cpu", "exemplars"])
        py_ok = sys.version_info[:2] in ((3, 11), (3, 12))
        self.assertEqual(checks["python"]["ok"], py_ok)
        if not py_ok:
            self.assertEqual(checks["python"]["install"], "uv venv --python 3.12")
        self.assertTrue(checks["provider"]["ok"])
        self.assertIn("rtf=", checks["provider"]["detail"])
        self.assertTrue(checks["exemplars"]["ok"])
        broken = self.work_dir / "broken-pack"
        make_pack(broken, broken=True)
        cp2 = run_script("preflight", "--json", "--provider", "null", cwd=self.work_dir, env={**os.environ, "MTV_EXEMPLARS": str(broken)})
        ex = {c["name"]: c for c in json.loads(cp2.stdout)["checks"]}["exemplars"]
        self.assertTrue(ex["ok"])
        self.assertEqual(ex["detail"], "3 findings (continuing without exemplars)")
        self.assertEqual(cp.returncode, 0 if report["ok"] else 1)
        self.assertEqual(report["ok"], all(c["ok"] for c in report["checks"]))


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
