"""Check every tool a run needs before it starts, with the command that installs each missing one.

A failing check stops the run. A missing font candidate and a broken exemplar pack only
report, because Text falls back to Pango's default serif and a run goes on without exemplars.
"""

from __future__ import annotations

import contextlib
import importlib
import json
import os
import platform
import shlex
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import exemplars
import narrate
from mtv import common

PROVIDER_TEXT = "One two three four five six seven eight nine ten."
MIN_FREE_BYTES = 5 * 1024**3
PYTHON_INSTALL = "uv venv --python 3.12"
# The skill's own copy, since a consumer project installs the skill outside the kit's tree.
MANIM_INSTALL = f"uv pip install -r {shlex.quote(str(Path(__file__).resolve().parent / 'requirements.txt'))}"
LATEX_INSTALL = (
    "apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended"
    " texlive-fonts-extra texlive-science dvisvgm"
)
FFMPEG_INSTALL = "apt-get install -y ffmpeg"
SCRIPTS_DIR = Path(__file__).resolve().parent


def provider_install(name: str) -> str | None:
    """The command that makes provider ``name`` work, with absolute paths, so it runs from any
    directory: install its requirements into this interpreter's venv, then speak one sentence
    (which fetches Kokoro's weights). None for the null provider, which needs nothing."""
    if name == "null":
        return None
    python = shlex.quote(sys.executable)
    requirements = ["requirements.txt"] + (["requirements-kokoro.txt"] if name == "kokoro" else [])
    install = f"uv pip install --python {python}" + "".join(
        f" -r {shlex.quote(str(SCRIPTS_DIR / r))}" for r in requirements
    )
    key = "set ELEVENLABS_API_KEY, then " if name == "elevenlabs" else ""
    warmup = f"{python} {shlex.quote(str(SCRIPTS_DIR / 'narrate.py'))} --warmup --provider {shlex.quote(name)}"
    return f"{key}{install} && {warmup}"


@dataclass
class Check:
    """One tool's result; ``install`` is the command that provides the tool, None where none does."""

    name: str
    ok: bool
    detail: str
    install: str | None


def run_checks(provider_name: str) -> list[Check]:
    manim_version, manim_error = _import_manim()
    return [
        _python_check(),
        Check("manim", (manim_version or "").startswith("0.22."), manim_version or manim_error, MANIM_INSTALL),
        _tool_check("latex", LATEX_INSTALL),
        _tool_check("dvisvgm", LATEX_INSTALL),
        _tool_check("ffmpeg", FFMPEG_INSTALL),
        _tool_check("ffprobe", FFMPEG_INSTALL),
        _provider_check(provider_name),
        _font_check(manim_version is not None),
        _disk_check(),
        Check("cpu", True, f"{os.cpu_count() or 'unknown'} CPUs", None),
        _exemplars_check(),
    ]


def _python_check() -> Check:
    return Check("python", sys.version_info[:2] in ((3, 11), (3, 12)), platform.python_version(), PYTHON_INSTALL)


def _import_manim() -> tuple[str | None, str]:
    """manim's version, or None and the reason it does not import."""
    try:
        return importlib.import_module("manim").__version__, ""
    # A broken install raises whatever its failing native dependency raises.
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _tool_check(tool: str, install: str) -> Check:
    path = common.which(tool)
    return Check(tool, path is not None, path or "not on PATH", install)


def _provider_check(name: str) -> Check:
    try:
        provider = narrate.build_provider(name, narrate.voice_for(name, None))
        rtf = narrate.time_synthesis(provider, PROVIDER_TEXT)
    # A provider fails with whatever its library raises, and a failure is reported, not raised.
    except Exception as exc:
        return Check("provider", False, f"{name}: {type(exc).__name__}: {exc}", provider_install(name))
    return Check("provider", True, f"{name} rtf={rtf:.3f}", provider_install(name))


def _font_check(manim_imports: bool) -> Check:
    # Passes without manim, whose own check already fails, so one missing tool is one failure.
    if not manim_imports:
        return Check("font", True, "skipped: manim absent", None)
    try:
        from mtv import look

        font = look.pick_font()
    # manimpango is a native extension, so a broken install raises anything.
    except Exception as exc:
        return Check("font", False, f"{type(exc).__name__}: {exc}", None)
    return Check("font", True, font or "Pango default serif (no FONT_CANDIDATES entry installed)", None)


def _disk_check() -> Check:
    free = shutil.disk_usage(".").free
    return Check("disk", free >= MIN_FREE_BYTES, f"{free / 1024**3:.1f} GiB free", None)


def _exemplars_check() -> Check:
    # A failed pack is a report.md warning and never a stop, so this check always passes.
    pack_dir = os.environ.get("MTV_EXEMPLARS")
    if not pack_dir:
        return Check("exemplars", True, "MTV_EXEMPLARS unset", None)
    findings = exemplars.check(Path(pack_dir))
    detail = f"{len(findings)} findings (continuing without exemplars)" if findings else "0 findings"
    return Check("exemplars", True, detail, None)


def main(argv: list[str] | None = None) -> int:
    description = "Check every tool a run needs, with an install line per missing one."
    parser = common.lesson_parser(description, positional=False)
    parser.add_argument("--json", action="store_true", help='print one line: {"ok": bool, "checks": [...]}')
    provider_help = f"narration provider to time; default {narrate.DEFAULT_PROVIDER}"
    parser.add_argument("--provider", default=narrate.DEFAULT_PROVIDER, help=provider_help)
    args = parser.parse_args(argv)
    # Once imported, manim logs to stdout (CE manim/_config/logger_utils.py:87,92-93), and so does
    # every library logging through its handler while the checks run, such as huggingface_hub's
    # requests as Kokoro loads. stdout carries only the report: --json's one line, or the verdict last.
    with contextlib.redirect_stdout(sys.stderr):
        checks = run_checks(args.provider)
    ok = all(check.ok for check in checks)
    if args.json:
        # A passing check needs no install command, so its install is null.
        rows = [{**asdict(check), "install": None if check.ok else check.install} for check in checks]
        print(json.dumps({"ok": ok, "checks": rows}))
        return 0 if ok else 1
    for check in checks:
        print(f"{check.name}: {'ok' if check.ok else 'FAIL'}, {check.detail}")
        if not check.ok and check.install:
            print(f"  install: {check.install}")
    failing = [check.name for check in checks if not check.ok]
    return common.verdict(ok, f"preflight: {len(checks)} checks" if ok else f"preflight: {', '.join(failing)}")


if __name__ == "__main__":
    sys.exit(main())
