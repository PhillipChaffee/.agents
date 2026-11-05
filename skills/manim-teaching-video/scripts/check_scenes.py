"""Lint the generated lesson.py against ManimCE and the lesson's contract, then dry-run it.

The lint reads the file's syntax tree, so a word in a comment or a docstring is never a
finding. A dry run executes every scene's construct without writing video, catching what
the tree cannot show before any render time is spent, so it runs only on a clean file.
"""

from __future__ import annotations

import ast
import os
import re
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

from mtv import common
from mtv import lesson as mtv_lesson

SCRIPTS_DIR = Path(__file__).resolve().parent
KIND_BASES = {"flat": "NarratedScene", "camera": "NarratedCameraScene", "3d": "Narrated3DScene"}
TAIL_LINES = 20
# Pango sets these classes' strings (positional or text=), so a number, sign or Greek letter in one prints
# in a different font from the same one in MathTex beside it; words are all they should hold.
TEXT_CLASSES = frozenset({"Text", "MarkupText", "Paragraph"})
# A digit, a math sign or a Greek letter: the ASCII signs = < > + ^ % \, the Latin-1 ± ² ³ µ ¹
# ¼ ½ ¾ × ÷, then whole blocks: Greek and Coptic (letters and symbols such as ϕ ϵ ϑ), the per
# mille and per ten thousand signs ‰ ‱ with the primes, superscripts and subscripts, vulgar
# fractions, arrows and mathematical operators (the minus sign \u2212 among them). A percent
# sign that stands for the word, as in guess a %, is still the sign MathTex sets as \%. The
# ASCII hyphen-minus and the other punctuation belong to words, as in non-linear, isn't or
# (sorted), and so do dashes, curly quotes, the ellipsis, the bullet and the middle dot
# captions use as a separator, which sit outside these blocks.
MATH_IN_TEXT = re.compile(
    r"[0-9=<>+^%\\\u00b1\u00b2\u00b3\u00b5\u00b9\u00bc-\u00be\u00d7\u00f7\u0370-\u03ff"
    r"\u2030-\u2037\u2070-\u209f\u2150-\u215f\u2190-\u21ff\u2200-\u22ff]"
)
# MarkupText's tags are markup, not text, and their attributes hold digits, = and %, as size="150%".
MARKUP_TAG = re.compile(r"<[^>]*>")
FORMAT_CALLS = frozenset({"str", "repr", "format"})
TEXT_ARG_CHARS = 40
CLOSING_QUOTES = re.compile(r"(\"\"\"|'''|\"|')\Z")
# A value formatted in, or a digit in a name such as GPT-2, can be a word, which MathTex is not for.
WORD_FIX = "or, when the value is a word or a name, reword it or build the string without formatting"
TEXT_FIX = (
    "put each number, sign and formula in MathTex (DecimalNumber or Integer when the value changes) "
    "and the words in Text, side by side in one VGroup(...).arrange(RIGHT, buff=0.15), "
    f'as in VGroup(Text("loss"), MathTex(r"\\approx 0.42")), {WORD_FIX}'
)
# The kit's question_caption(target, text) (mtv/patterns.py) sets its question in Text too.
CAPTION_HELPER = "question_caption"
CAPTION_FIX = (
    "question_caption sets the question in Text, so spell the numbers and signs out in words, "
    f"or move them into a MathTex beside the caption, {WORD_FIX}"
)
# A letter alone cannot be told from a word, but one the file also sets in math is that symbol,
# shown in two typefaces. MathTex sets all its strings in math, Tex only between $ signs.
MATH_CLASSES = frozenset({"MathTex", "SingleStringMathTex"})
TEX_CLASS = "Tex"
TEX_MATH_SHIFT = re.compile(r"(?<!\\)\$\$?")
# A text-mode command's braced argument (one brace level deep) holds words, and a command name,
# as \frac, or an escaped sign, as \%, holds no symbol.
TEX_WORDS = re.compile(r"\\(?:text[a-z]*|mbox|operatorname)\*?\s*\{(?:[^{}]|\{[^{}]*\})*\}")
TEX_COMMAND = re.compile(r"\\(?:[A-Za-z]+|.)")
# A Latin letter with no letter beside it; an apostrophe or a dot between letters joins them into
# one word, as in isn't, model's or e.g.
LONE_LETTER = re.compile(r"(?<![^\W\d_])(?<![^\W\d_]['’.])[A-Za-z](?![^\W\d_])(?!['’.][^\W\d_])")
WORD_LETTERS = frozenset("aAI")
# LaTeX sets these function names upright as operators, and \operatorname sets any name so: a name the
# file sets that way is that function wherever it stands alone in Text, shown in two typefaces.
OPERATOR_NAMES = frozenset(
    "sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln lg exp max min arg det lim sup inf gcd "
    "deg dim ker Pr".split()
)
TEX_OPERATORNAME = re.compile(r"\\operatorname\*?\s*\{\s*([A-Za-z]+)\s*\}")
# A run of letters is one word, so a name stands alone only as a whole run: cos in cosine is not the name.
LETTER_RUN = re.compile(r"[^\W\d_]+")


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


def _text_parts(node: ast.expr) -> tuple[str, bool]:
    """The literal text of a text argument, and whether a value is formatted into it.

    A + concatenation is read as its parts. A name, attribute or subscript holds a value the
    tree cannot show, so it adds no text and is not judged.
    """
    if isinstance(node, ast.Constant):
        return (node.value, False) if isinstance(node.value, str) else ("", False)
    if isinstance(node, ast.JoinedStr):
        text = "".join(value.value for value in node.values if isinstance(value, ast.Constant))
        return text, any(isinstance(value, ast.FormattedValue) for value in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        (left, left_formatted), (right, right_formatted) = _text_parts(node.left), _text_parts(node.right)
        return left + right, left_formatted or right_formatted
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return "", True
    if isinstance(node, ast.Call):
        func = node.func
        return "", (isinstance(func, ast.Name) and func.id in FORMAT_CALLS) or (
            isinstance(func, ast.Attribute) and func.attr == "format"
        )
    return "", False


def _shown_text(node: ast.expr, markup: bool) -> tuple[str, bool]:
    text, formatted = _text_parts(node)
    return (MARKUP_TAG.sub("", text) if markup else text), formatted


def _sets_math(node: ast.expr, markup: bool) -> bool:
    text, formatted = _shown_text(node, markup)
    return formatted or MATH_IN_TEXT.search(text) is not None


def _callee(node: ast.AST) -> str | None:
    """The name ``node`` calls, by name or through its module, as Text or manim.Text; None if not a call."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def _math_texts(tree: ast.Module) -> Iterator[str]:
    """The math each MathTex, SingleStringMathTex or Tex call in the file sets, one string per call."""
    for node in ast.walk(tree):
        callee = _callee(node)
        if callee not in MATH_CLASSES and callee != TEX_CLASS:
            continue
        # ManimCE joins MathTex's strings with a space, and Tex's with nothing but a marker between
        # them, so Tex("$x", "y$") sets xy while Tex("$x$", "$y$") sets two formulas: a NUL keeps the
        # strings apart for the $ split and is dropped from the math it finds.
        tex = ("\0" if callee == TEX_CLASS else " ").join(_text_parts(arg)[0] for arg in node.args)
        yield " ".join(TEX_MATH_SHIFT.split(tex)[1::2]).replace("\0", "") if callee == TEX_CLASS else tex


def _math_symbols(tree: ast.Module) -> set[str]:
    """The letters the file sets alone in math, as n in MathTex(r"\\log_2 n"), but not a or I."""
    symbols = set()
    for math in _math_texts(tree):
        symbols.update(LONE_LETTER.findall(TEX_COMMAND.sub(" ", TEX_WORDS.sub(" ", math))))
    return symbols - WORD_LETTERS


def _math_operators(tree: ast.Module) -> dict[str, str]:
    """The function names the file sets as operators in math, each with its command, as cos with \\cos.

    A command is read whole, so \\cosh sets cosh and no cos, and \\text{max} sets no max.
    """
    operators = {}
    for math in _math_texts(tree):
        for name in TEX_OPERATORNAME.findall(math):
            operators.setdefault(name, f"\\operatorname{{{name}}}")
        for command in TEX_COMMAND.findall(math):
            if command[1:] in OPERATOR_NAMES:
                operators.setdefault(command[1:], command)
    return operators


def _listed(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def _twin_fix(subject: str, one: bool, caption: bool, reword: str, wrapper: str = "") -> str:
    """The fix for what ``subject`` names, set in Text and as math elsewhere in the file.

    ``wrapper`` names the file's own function that sets it in Text, and ``reword`` when it is a word.
    """
    it = "it" if one else "them"
    where = (f"and question_caption sets the question in Text, so set {it} in a MathTex beside the caption"
             if caption else f"{wrapper}so set {it} in MathTex beside the words' Text")
    return (f"{subject} set as math elsewhere in the file, {where}, "
            f"in one VGroup(...).arrange(RIGHT, buff=0.15), or, when {reword}, reword it")


def _symbol_fix(letters: list[str], caption: bool) -> str:
    one, named = len(letters) == 1, _listed(letters)
    symbol = f"the letter {named} is the symbol {named}" if one else f"the letters {named} are the symbols {named}"
    # The file may set the letter in MathTex or between a Tex string's $ signs. A letter can also be
    # a word or a label, as the B of plan B, which MathTex is not for.
    letter = "the letter" if one else "a letter"
    return _twin_fix(symbol, one, caption, f"{letter} is a word or a label (plan B, part b)")


def _operator_fix(names: list[str], operators: dict[str, str], caption: bool, wrapper: str = "") -> str:
    one, commands = len(names) == 1, _listed([operators[name] for name in names])
    function = (f"the name {names[0]} is the function {commands}" if one
                else f"the names {_listed(names)} are the functions {commands}")
    # A function name used as a row label is still the function; max in max speed is a word.
    name = "the name" if one else "a name"
    return _twin_fix(function, one, caption, f"{name} is an English word, as in max speed", wrapper)


def _names(texts: list[str], operators: dict[str, str]) -> list[str]:
    """The function names in ``operators`` standing alone in ``texts``, each once, in the order they come."""
    return [*dict.fromkeys(word for text in texts for word in LETTER_RUN.findall(text) if word in operators)]


def _set_strings(node: ast.Call, callee: str) -> list[ast.expr]:
    """The strings a Text, MarkupText, Paragraph or question_caption call sets.

    The text keyword is the string being set too; the other keywords style it and are not
    judged, nor is question_caption's first argument, its target.
    """
    positional = node.args[1:2] if callee == CAPTION_HELPER else node.args
    return [*positional, *(keyword.value for keyword in node.keywords if keyword.arg == "text")]


Wrapped = tuple[int | None, str, bool]


def _wrappers(tree: ast.Module) -> dict[str, frozenset[Wrapped]]:
    """The file's own functions that set a parameter in Text, each with the parameters it sets there.

    A parameter is its position (None when keyword-only), its name and whether MarkupText sets it.
    It counts only when the caller's string reaches the call unchanged: one assigned in the body, or
    bound again by a nested function's own parameter, may hold another. A name defined more than
    once keeps the parameters every definition sets, and a method is left out, since a call reaches
    it through self or cls with one argument fewer than it has parameters.
    """
    methods = {id(node) for cls in ast.walk(tree) if isinstance(cls, ast.ClassDef) for node in cls.body}
    wrappers: dict[str, frozenset[Wrapped]] = {}
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef) or id(function) in methods:
            continue
        positional = [arg.arg for arg in (*function.args.posonlyargs, *function.args.args)]
        parameters = {*positional, *(arg.arg for arg in function.args.kwonlyargs)}
        inside = list(ast.walk(function))
        bound = [node.arg for node in inside if isinstance(node, ast.arg)]
        stored = {node.id for node in inside if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
        sets = set()
        for node in inside:
            callee = _callee(node)
            if callee not in TEXT_CLASSES and callee != CAPTION_HELPER:
                continue
            for arg in _set_strings(node, callee):
                if (isinstance(arg, ast.Name) and arg.id in parameters and bound.count(arg.id) == 1
                        and arg.id not in stored):
                    position = positional.index(arg.id) if arg.id in positional else None
                    sets.add((position, arg.id, callee == "MarkupText"))
        wrappers[function.name] = wrappers.get(function.name, frozenset(sets)) & sets
    return {name: sets for name, sets in wrappers.items()
            if sets and name not in TEXT_CLASSES and name != CAPTION_HELPER}


def _wrapper_strings(node: ast.Call, wrapped: frozenset[Wrapped]) -> list[tuple[str, ast.expr, bool]]:
    """The strings a call to a wrapper passes on to Text, each with its parameter's name and markup."""
    # A starred argument stands for any number of arguments, so no position after it is known.
    starred = next((i for i, arg in enumerate(node.args) if isinstance(arg, ast.Starred)), len(node.args))
    keywords = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg is not None}
    strings = []
    for position, name, markup in sorted(wrapped, key=lambda item: (item[0] is None, item[0] or 0, item[1:])):
        if position is not None and position < starred:
            strings.append((name, node.args[position], markup))
        elif name in keywords:
            strings.append((name, keywords[name], markup))
    return strings


def _written(source: str, node: ast.AST) -> str:
    """``node`` as the file writes it, on one line and cut to TEXT_ARG_CHARS characters.

    A cut string keeps its closing quotes, so the name still reads as the literal it cuts.
    """
    text = re.sub(r"\s*\n\s*", " ", ast.get_source_segment(source, node) or ast.unparse(node))
    if len(text) <= TEXT_ARG_CHARS:
        return text
    close = CLOSING_QUOTES.search(text)
    end = close.group() if close else ""
    return text[: TEXT_ARG_CHARS - 3 - len(end)] + "..." + end


def _set_text_fix(node: ast.Call, callee: str, symbols: set[str], operators: dict[str, str]) -> str | None:
    """The fix for a Text, MarkupText, Paragraph or question_caption call, or None when it sets only words.

    A call setting a number gets that finding alone; one setting none is then read for a letter the
    file sets in math, and one setting neither for a function name the file sets in math.
    """
    markup, caption = callee == "MarkupText", callee == CAPTION_HELPER
    judged = _set_strings(node, callee)
    if any(_sets_math(arg, markup) for arg in judged):
        return CAPTION_FIX if caption else TEXT_FIX
    texts = [_shown_text(arg, markup)[0] for arg in judged]
    found = (letter for text in texts for letter in LONE_LETTER.findall(text))
    if letters := [*dict.fromkeys(letter for letter in found if letter in symbols)]:
        return _symbol_fix(letters, caption)
    if names := _names(texts, operators):
        return _operator_fix(names, operators, caption)
    return None


def _wrapper_fix(node: ast.Call, callee: str, wrapped: frozenset[Wrapped], operators: dict[str, str]) -> str | None:
    """The fix for a call to the file's own function that passes a function name on to Text, or None."""
    hits = [(param, _names([_shown_text(arg, markup)[0]], operators))
            for param, arg, markup in _wrapper_strings(node, wrapped)]
    if not (names := [*dict.fromkeys(name for _, found in hits for name in found)]):
        return None
    params = [*dict.fromkeys(param for param, found in hits if found)]
    arguments = "argument" if len(params) == 1 else "arguments"
    return _operator_fix(names, operators, False, f"and {callee} sets its {_listed(params)} {arguments} in Text, ")


def _text_findings(tree: ast.Module, source: str, filename: str) -> list[dict]:
    # The class or helper may be imported by name or reached through its module, as manim.Text, and
    # the file's own wrapper is called by its name. A wrapper's strings are read for function names
    # only; the number and letter readings keep to the classes' and the helper's own calls.
    symbols, operators, wrappers = _math_symbols(tree), _math_operators(tree), _wrappers(tree)
    findings = []
    for node in ast.walk(tree):
        callee = _callee(node)
        if callee in TEXT_CLASSES or callee == CAPTION_HELPER:
            fix, keywords = _set_text_fix(node, callee, symbols, operators), {"text"}
        elif callee in wrappers and isinstance(node.func, ast.Name):
            wrapped = wrappers[callee]
            fix, keywords = _wrapper_fix(node, callee, wrapped, operators), {param for _, param, _ in wrapped}
        else:
            continue
        if fix is None:
            continue
        shown = [*node.args, *(keyword for keyword in node.keywords if keyword.arg in keywords)]
        name = f"{_written(source, node.func)}({', '.join(_written(source, part) for part in shown)})"
        findings.append(_finding(filename, node.lineno, name, fix))
    return findings


def lint_source(source: str, lesson: dict, filename: str = "lesson.py") -> list[dict]:
    tree, findings = _parse(source, filename)
    if tree is not None:
        findings += _call_findings(tree, filename)
        findings += _text_findings(tree, source, filename)
        findings += _color_findings(tree, lesson, filename)
        findings += _class_findings(tree, lesson, filename)
    return _one_per_line(findings)


def dry_run(lesson_py: Path, classes: list[str], cwd: Path, lesson_path: Path) -> dict[str, bool]:
    """``manim render --dry_run`` once per class, with the draft render's config; True where it exits 0.

    A dry run still executes construct, whose load_lesson finds the lesson through
    MTV_LESSON, and it writes no run log, so MTV_RUN_LOG is left out. It also draws every
    frame, so the draft config keeps it to the frames step 7's draft render draws, at 854x480
    and 15 fps rather than CE's default 1920x1080 and 60. A failed run's last lines go to
    stdout, so the manim error text precedes the verdict. Like a render, a run is killed and
    fails once its output has not grown for common.HANG_TIMEOUT_S, so a construct that never
    ends cannot hold up the check while a long one that keeps drawing finishes.
    """
    env = {key: value for key, value in os.environ.items() if key != "MTV_RUN_LOG"}
    env.update(PYTHONPATH=common.scripts_pythonpath(SCRIPTS_DIR), MTV_LESSON=str(lesson_path.resolve()))
    hang_timeout_s = common.HANG_TIMEOUT_S
    results = {}
    with tempfile.TemporaryDirectory(prefix="mtv-dry-run-") as logs:
        for scene_class in classes:
            # CE global options, manim/cli/render/global_options.py:60,112; the class goes last.
            argv = ["manim", "render", "--config_file", str(common.config_file("draft")), "--dry_run",
                    str(lesson_py.resolve()), scene_class]
            log, failure = Path(logs) / f"{scene_class}.log", "dry run failed"
            try:
                returncode, _ = common.run_with_watchdog(argv, env=env, cwd=cwd, log=log, hang_timeout_s=hang_timeout_s)
            # A manim found on PATH can still fail to start, as from a moved venv's shebang.
            except OSError as exc:
                ok, output = False, str(exc)
            else:
                ok, output = returncode == 0, log.read_text(encoding="utf-8", errors="replace")
                if returncode is None:
                    failure = (f"dry run produced no output for {hang_timeout_s:g} s"
                               " | fix: end the loop, or cut the work, in construct")
            results[scene_class] = ok
            if not ok:
                print(f"{scene_class}: {failure}")
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
