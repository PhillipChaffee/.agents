"""Lint the generated lesson.py against ManimCE and the lesson's contract, then dry-run it.

The lint reads the file's syntax tree, so a word in a comment or a docstring is never a
finding. A dry run executes every scene's construct without writing video, catching what
the tree cannot show before any render time is spent, so it runs only on a clean file.
"""

from __future__ import annotations

import ast
import os
import sys
from collections.abc import Iterator
from pathlib import Path

from mtv import common
from mtv import lesson as mtv_lesson

SCRIPTS_DIR = Path(__file__).resolve().parent
KIND_BASES = {"flat": "NarratedScene", "camera": "NarratedCameraScene", "3d": "Narrated3DScene"}
TAIL_LINES = 20


def _finding(filename: str, line: int | None, name: str, fix: str) -> dict:
    return {"file": filename, "line": line, "name": name, "fix": fix}


def _used_names(tree: ast.AST) -> Iterator[tuple[int, str]]:
    """Every name ``tree`` reads, binds, imports or passes as a keyword, with its line."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            yield node.lineno, node.id
        elif isinstance(node, ast.Attribute):
            yield node.lineno, node.attr
        elif isinstance(node, ast.keyword) and node.arg is not None:
            yield node.lineno, node.arg
        elif isinstance(node, ast.alias):
            yield from ((node.lineno, part) for part in node.name.split("."))
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield from ((node.lineno, part) for part in node.module.split("."))


def _parse(source: str, filename: str) -> tuple[ast.Module | None, list[dict]]:
    """The tree of ``source`` with its banned-name findings, or None and one syntax-error finding."""
    try:
        tree = ast.parse(source, filename)
    # Python 3.11 reports a NUL byte in the source as ValueError, 3.12 as SyntaxError.
    except (SyntaxError, ValueError) as exc:
        return None, [_finding(filename, getattr(exc, "lineno", None), "syntax error", getattr(exc, "msg", str(exc)))]
    findings = [
        _finding(filename, line, name, common.BANNED_NAMES[name])
        for line, name in _used_names(tree)
        if name in common.BANNED_NAMES
    ]
    return tree, findings


def _one_per_line(findings: list[dict]) -> list[dict]:
    # A name used twice on a line needs one fix, and the reader fixes the file top to bottom;
    # a class missing from the file has no line and comes first.
    unique = {(finding["line"], finding["name"]): finding for finding in findings}
    return sorted(unique.values(), key=lambda finding: finding["line"] or 0)


def banned_findings(source: str, filename: str = "lesson.py") -> list[dict]:
    return _one_per_line(_parse(source, filename)[1])


def _base_names(node: ast.ClassDef) -> set[str]:
    # A base may be imported by name or reached through its module, as mtv.narrated.NarratedScene.
    return {
        base.id if isinstance(base, ast.Name) else base.attr
        for base in node.bases
        if isinstance(base, (ast.Name, ast.Attribute))
    }


def _call_findings(tree: ast.Module, filename: str) -> list[dict]:
    findings = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "frame"
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        ):
            findings.append(_finding(filename, node.lineno, "self.frame", "self.camera.frame in a NarratedCameraScene"))
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "play"
            and any(isinstance(arg, ast.Attribute) for arg in node.args)
        ):
            findings.append(_finding(filename, node.lineno, "play(mob.method)", "self.play(mob.animate.method(...))"))
    return findings


def _color_findings(tree: ast.Module, lesson: dict, filename: str) -> list[dict]:
    contract = set(lesson.get("colors", {}).values())
    fix = f"use a lesson colors value: {', '.join(sorted(contract))}"
    return [
        _finding(filename, node.lineno, node.id, fix)
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id in common.COLOR_NAMES
        and node.id not in contract
        and node.id not in common.NEUTRAL_COLORS
    ]


def _class_findings(tree: ast.Module, lesson: dict, filename: str) -> list[dict]:
    # manim finds scenes among the module's own members (CE manim/utils/module_ops.py:71-84),
    # so a class nested anywhere else cannot be rendered.
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    findings = []
    for scene in lesson.get("scenes", []):
        name, kind = scene["scene_class"], scene["scene_kind"]
        node, base = classes.get(name), KIND_BASES[kind]
        if node is None:
            findings.append(_finding(filename, None, name, f"define class {name}"))
        elif base not in _base_names(node):
            findings.append(_finding(filename, node.lineno, name, f"subclass {base} for scene_kind '{kind}'"))
    for node in classes.values():
        # zoom_to needs a NarratedCameraScene and orbit_with_hud a Narrated3DScene; no scene is both.
        if {"zoom_to", "orbit_with_hud"} <= {used for _, used in _used_names(node)}:
            findings.append(_finding(filename, node.lineno, "zoom_to+orbit_with_hud", "one camera idiom per scene"))
    return findings


def lint_source(source: str, lesson: dict, filename: str = "lesson.py") -> list[dict]:
    tree, findings = _parse(source, filename)
    if tree is not None:
        findings += _call_findings(tree, filename)
        findings += _color_findings(tree, lesson, filename)
        findings += _class_findings(tree, lesson, filename)
    return _one_per_line(findings)


def dry_run(lesson_py: Path, classes: list[str], cwd: Path, lesson_path: Path) -> dict[str, bool]:
    """``manim render --dry_run`` once per class; True where it exits 0.

    A dry run still executes construct, whose load_lesson finds the lesson through
    MTV_LESSON, and it writes no run log, so MTV_RUN_LOG is left out. A failed run's last
    lines go to stdout, so the manim error text precedes the verdict.
    """
    env = {key: value for key, value in os.environ.items() if key != "MTV_RUN_LOG"}
    env.update(PYTHONPATH=common.scripts_pythonpath(SCRIPTS_DIR), MTV_LESSON=str(lesson_path.resolve()))
    results = {}
    for scene_class in classes:
        # CE global option, manim/cli/render/global_options.py:112; the class goes last.
        argv = ["manim", "render", "--dry_run", str(lesson_py.resolve()), scene_class]
        try:
            completed = common.run_cmd(argv, env=env, cwd=cwd)
            ok, output = completed.returncode == 0, completed.stdout + completed.stderr
        # A manim found on PATH can still fail to start, as from a moved venv's shebang.
        except OSError as exc:
            ok, output = False, str(exc)
        results[scene_class] = ok
        if not ok:
            print(f"{scene_class}: dry run failed")
            for line in output.splitlines()[-TAIL_LINES:]:
                print(line)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Lint the generated lesson.py, then dry-run each scene class.", positional=False)
    parser.add_argument("lesson_py", type=Path, help="path to the generated lesson.py")
    parser.add_argument("lesson", type=Path, help="path to lesson.json")
    args = parser.parse_args(argv)
    lesson, errors = common.load_valid_lesson(args.lesson)
    # validate leaves both storyboard fields optional, and the class check reads them.
    errors = errors or [
        f"{scene['id']}: missing field '{field}'"
        for scene in lesson.get("scenes", [])
        for field in ("scene_class", "scene_kind")
        if field not in scene
    ]
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    try:
        source = args.lesson_py.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return common.usage_error(f"cannot read {args.lesson_py}: {getattr(exc, 'strerror', None) or exc}")
    findings = lint_source(source, lesson, str(args.lesson_py))
    for finding in findings:
        print(f"{finding['file']}:{finding['line'] or '-'} {finding['name']} | fix: {finding['fix']}")
    # A finding fails the gate whatever the environment, so manim matters only for a clean file.
    has_manim = common.which("manim") is not None
    results = {}
    if not findings and has_manim:
        classes = [scene["scene_class"] for scene in lesson.get("scenes", [])]
        results = dry_run(args.lesson_py, classes, args.lesson.resolve().parent, args.lesson)
    ok = not findings and has_manim and all(results.values())
    lesson.setdefault("checks", {})["scenes"] = {
        "pass": ok,
        "at": common.now_iso(),
        "findings": findings,
        "dry_run": results,
    }
    mtv_lesson.save(lesson, args.lesson)
    if not findings and not has_manim:
        return common.usage_error("manim is not on PATH, so the dry run cannot run; activate the venv that has ManimCE")
    summary = f"scenes: {len(findings)} findings"
    if results:
        summary += f", {sum(results.values())} of {len(results)} dry runs passed"
    return common.verdict(ok, summary)


if __name__ == "__main__":
    sys.exit(main())
