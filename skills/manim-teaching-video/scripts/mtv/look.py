"""The lesson's look: the TeX template, the text font, the role colors and the black background.

manim.cfg leaves ``tex_template`` empty on purpose, so the template is set here in code, once
per scene, by ``apply``; NarratedMixin.load_lesson calls it.
"""

from __future__ import annotations

from manim import BLACK, Scene, TexTemplate, TexTemplateLibrary, Text, config

from .common import ROLE_COLORS

__all__ = ["FONT_CANDIDATES", "ROLE_COLORS", "TEMPLATE", "apply", "pick_font"]

# The threeb1b preamble (CE manim/utils/tex_templates.py:64-67), plus the one macro the
# lesson's formulas use for a typographic minus.
TEMPLATE: TexTemplate = TexTemplateLibrary.threeb1b.copy()
TEMPLATE.add_to_preamble(r"\newcommand{\minus}{-}")

# Serif faces that sit beside Computer Modern math, most to least alike.
FONT_CANDIDATES = ("CMU Serif", "Latin Modern Roman", "TeX Gyre Termes", "DejaVu Serif")


def pick_font() -> str:
    """The first of FONT_CANDIDATES that Pango can find, else "" (Pango's default face)."""
    import manimpango

    available = set(manimpango.list_fonts())
    return next((font for font in FONT_CANDIDATES if font in available), "")


def apply(scene: Scene) -> None:
    """Give ``scene`` the lesson's background, TeX template and text font."""
    config.background_color = BLACK  # CE manim/_config/utils.py:1203-1209
    # The scene's camera read the config when the scene was built, before construct calls
    # this (CE manim/camera/camera.py:134-139), so its background is set directly; the
    # setter redraws it (CE manim/camera/camera.py:172-175).
    scene.camera.background_color = BLACK
    # MathTex reads config["tex_template"] when it is built (CE manim/mobject/text/tex_mobject.py:76-77).
    config.tex_template = TEMPLATE  # CE manim/_config/utils.py:1768-1782
    Text.set_default(font=pick_font())  # CE manim/mobject/mobject.py:261-268
