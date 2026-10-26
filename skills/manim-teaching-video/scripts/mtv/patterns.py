"""The sixteen pattern helpers: the only Manim building blocks a generated scenes file imports.

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

Each helper's docstring opens with its one-line contract from the pattern index, which is
what the scene coder reads. Every number renders through DecimalNumber or MathTex, and every
color comes from the lesson's role palette, so check_scenes.py's color contract holds.
"""

from __future__ import annotations

import contextlib
import math
import random
from collections.abc import Iterable, Iterator

import manim
from manim import (
    DOWN,
    ITALIC,
    PURE_YELLOW,
    RIGHT,
    UP,
    Animation,
    AnimationGroup,
    Arrow,
    DecimalNumber,
    Dot,
    FadeIn,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    ReplacementTransform,
    Restore,
    ShowPassingFlash,
    Square,
    Succession,
    Text,
    ValueTracker,
    VGroup,
    VMobject,
    Wait,
    linear,
    there_and_back,
)

from .common import CLOCK_EPSILON_S, FRAME_HEIGHT, FRAME_WIDTH
from .look import ROLE_COLORS
from .narrated import Narrated3DScene, NarratedCameraScene

__all__ = [
    "LayeredNetwork", "NumericColumn", "WeightGrid", "provenance", "numbers_to_symbol",
    "save_and_restore_layout", "flash_along", "focus_and_dim", "nudge_and_return",
    "count_parameters", "live_decimal", "zoom_to", "orbit_with_hud", "staggered", "delayed",
    "question_caption",
]

# A layer taller than this shows its first and last halves with a vertical ellipsis between.
_MAX_SHOWN_NODES = 16


def _sign_color(value: float) -> manim.ManimColor:
    """The role color of a weight's sign, resolved from its CE constant name."""
    return getattr(manim, ROLE_COLORS["weight_pos" if value >= 0 else "weight_neg"])


class LayeredNetwork(VGroup):
    """A layered network with seeded weights colored by sign, ``.layers``, ``.edges``, ``.node(l, i)``.

    ``sizes`` counts each layer's nodes left to right; a layer of more than 16 shows 16 dots
    with a vertical ellipsis between its halves, and ``node`` indexes the shown dots. Each
    edge's color is its weight's sign and its stroke opacity the weight's magnitude, with the
    weights drawn from ``random.Random(seed)``, so a seed fixes the picture. A full layer is
    about 10 units tall at scale 1, more than the 8-unit frame, so scale the network to fit.
    """

    def __init__(self, sizes: list[int], seed: int, **kwargs) -> None:
        super().__init__(**kwargs)
        rng = random.Random(seed)
        self._nodes: list[list[Dot]] = []
        self.layers: list[VGroup] = []
        for size in sizes:
            shown = min(size, _MAX_SHOWN_NODES)
            dots = [Dot(radius=0.12) for _ in range(shown)]  # CE manim/mobject/geometry/arc.py:789-800
            members: list[Mobject] = list(dots)
            if size > _MAX_SHOWN_NODES:
                members.insert(shown // 2, MathTex(r"\vdots"))
            self._nodes.append(dots)
            self.layers.append(VGroup(*members).arrange(DOWN, buff=0.35))
        VGroup(*self.layers).arrange(RIGHT, buff=1.6)
        self.edges = VGroup()
        for left, right in zip(self._nodes, self._nodes[1:]):
            for a in left:
                for b in right:
                    weight = rng.uniform(-1, 1)
                    edge = Line(a.get_center(), b.get_center(), stroke_width=1.5)  # CE manim/mobject/geometry/line.py:65-100
                    self.edges.add(edge.set_stroke(_sign_color(weight), opacity=abs(weight)))
        # Edges first, so the nodes are drawn over them.
        self.add(self.edges, *self.layers)

    def node(self, layer: int, index: int) -> Dot:
        """The ``index``-th shown dot of layer ``layer``."""
        return self._nodes[layer][index]


class NumericColumn(VGroup):
    """A vertical column of ``DecimalNumber``, ``.at(i)``."""

    def __init__(self, values: list[float], decimals: int = 2, **kwargs) -> None:
        # CE manim/mobject/text/numbers.py:83-100
        super().__init__(*(DecimalNumber(v, num_decimal_places=decimals) for v in values), **kwargs)
        self.arrange(DOWN, buff=0.25)

    def at(self, index: int) -> DecimalNumber:
        """The number in row ``index``."""
        return self[index]


class WeightGrid(VGroup):
    """A grid of squares filled by sign and magnitude.

    ``shape`` is (rows, columns) and ``values`` fill it row by row; ValueError when their
    counts differ. A magnitude of 1 or more fills a square fully.
    """

    def __init__(self, values: list[float], shape: tuple[int, int], **kwargs) -> None:
        rows, cols = shape
        if len(values) != rows * cols:
            raise ValueError(f"WeightGrid: {len(values)} values do not fill a {rows}x{cols} grid")
        # CE manim/mobject/geometry/polygram.py:690-700; set_fill at vectorized_mobject.py:282.
        squares = (
            Square(side_length=0.25, stroke_width=0.5).set_fill(_sign_color(v), opacity=min(abs(v), 1.0)) for v in values
        )
        super().__init__(*squares, **kwargs)
        self.arrange_in_grid(rows=rows, cols=cols, buff=0.02)


def provenance(src: Mobject, dst: Mobject, run_time: float = 2.0) -> Animation:
    """``ReplacementTransform`` of a copy of ``src`` into ``dst``, the source stays."""
    return ReplacementTransform(src.copy(), dst, run_time=run_time)  # CE manim/animation/transform.py:253


def numbers_to_symbol(column: VGroup, symbol: MathTex, run_time: float = 2.0) -> Animation:
    """The column's digits collapse into the symbol by transforming copies."""
    return ReplacementTransform(column.copy(), symbol, run_time=run_time)


@contextlib.contextmanager
def save_and_restore_layout(scene, group: VGroup) -> Iterator[None]:
    """Saves ``group`` state, yields, restores with ``Restore`` on exit."""
    group.save_state()  # CE manim/mobject/mobject.py:2272
    yield
    scene.play(Restore(group))  # CE manim/animation/transform.py:598-625


def flash_along(path: VMobject, color=PURE_YELLOW, time_width: float = 1.0) -> Animation:
    """``ShowPassingFlash`` along a copy of the path."""
    # CE manim/animation/indication.py:274-316
    return ShowPassingFlash(path.copy().set_stroke(color, 6, opacity=1.0), time_width=time_width)


def focus_and_dim(group: VGroup, keep: list[Mobject], opacity: float = 0.2) -> Animation:
    """Everything in ``group`` but ``keep`` fades to ``opacity``, nothing is removed.

    ``keep`` may name mobjects nested at any depth, such as ``network.node(1, 3)``: a member
    holding one is opened up and only its other parts fade. ValueError when nothing would
    fade, since an empty play is a CE error.
    """
    dimmed = _dim_targets(group, keep)
    if not dimmed:
        raise ValueError("focus_and_dim: every member of group is in keep, so nothing would dim")
    # CE manim/mobject/types/vectorized_mobject.py:478, manim/animation/composition.py:30
    return AnimationGroup(*(m.animate.set_opacity(opacity) for m in dimmed))


def _dim_targets(group: Mobject, keep: list[Mobject]) -> list[Mobject]:
    """The largest parts of ``group`` that neither are nor hold anything in ``keep``."""
    targets = []
    for member in group.submobjects:
        if any(member is k for k in keep):
            continue
        family = member.get_family()
        if any(any(m is k for m in family) for k in keep):
            targets += _dim_targets(member, keep)
        else:
            targets.append(member)
    return targets


def nudge_and_return(mob: Mobject, amount: float = 0.1) -> Animation:
    """A small tremor and return, for "what if this knob moves".

    It lasts 1 s; ``self.play(nudge_and_return(knob), run_time=b.until(mark))`` times it to a mark.
    """
    # CE manim/mobject/mobject.py:313, manim/utils/rate_functions.py:216; built, so it is an
    # Animation with a run_time that delayed and AnimationGroup can read.
    return mob.animate(rate_func=there_and_back, run_time=1.0).shift(amount * UP).build()


def count_parameters(network: LayeredNetwork) -> tuple[DecimalNumber, Animation]:
    """A counter that increments as edges light up.

    Returns the counter, to be placed and added by the scene, and the 3 s animation that
    counts to the number of edges while each edge brightens to full opacity in turn.
    """
    tracker = ValueTracker(0)  # CE manim/mobject/value_tracker.py:21,83-97
    counter = DecimalNumber(0, num_decimal_places=0)
    counter.add_updater(lambda d: d.set_value(tracker.get_value()))
    # CE manim/animation/composition.py:297-349
    lighting = LaggedStart(*(edge.animate.set_stroke(opacity=1.0) for edge in network.edges), lag_ratio=0.1)
    # The group stretches its parts in proportion to fit 3 s, so the count gets the lighting's
    # own length and pace: unstretched it would be done before the first few edges lit.
    counting = tracker.animate(run_time=lighting.run_time, rate_func=linear).set_value(len(network.edges))
    # group=network: played, the group puts the network itself in the scene, not a new Group
    # holding the edges and the tracker, which would draw the edges over the nodes and give
    # the run log a box stretching to the tracker's value.
    return counter, AnimationGroup(counting, lighting, group=network, run_time=3.0)


def live_decimal(tracker: ValueTracker, decimals: int = 2) -> DecimalNumber:
    """An always-redrawn decimal bound to a tracker."""
    number = DecimalNumber(tracker.get_value(), num_decimal_places=decimals)
    number.add_updater(lambda d: d.set_value(tracker.get_value()))
    return number


def zoom_to(scene: NarratedCameraScene, mob: Mobject, margin: float = 0.5, run_time: float = 2.0) -> Animation:
    """Frame animates to fit ``mob``; requires ``NarratedCameraScene``.

    The frame keeps its aspect ratio and fits ``mob`` plus ``margin`` on every side.
    """
    if not isinstance(scene, NarratedCameraScene):
        raise TypeError("zoom_to needs a NarratedCameraScene")
    width = max(mob.width + 2 * margin, (mob.height + 2 * margin) * FRAME_WIDTH / FRAME_HEIGHT)
    # CE manim/scene/moving_camera_scene.py:17-47
    return scene.camera.frame.animate(run_time=run_time).set(width=width).move_to(mob)


def orbit_with_hud(scene: Narrated3DScene, hud: VGroup, degrees: float = 60.0, run_time: float = 10.0) -> None:
    """Ambient camera rotation while ``hud`` stays fixed in frame; requires ``Narrated3DScene``.

    It plays: the camera turns ``degrees`` over ``run_time`` seconds, so call it inside a beat
    with a ``run_time`` the beat has room for.
    """
    if not isinstance(scene, Narrated3DScene):
        raise TypeError("orbit_with_hud needs a Narrated3DScene")
    scene.add_fixed_in_frame_mobjects(*hud)  # CE manim/scene/three_d_scene.py:357
    scene.begin_ambient_camera_rotation(rate=math.radians(degrees) / run_time)  # :102
    scene.wait(run_time)
    scene.stop_ambient_camera_rotation()  # :140


def staggered(mobs: Iterable[Mobject], anim=FadeIn, lag_ratio: float = 0.5, run_time: float = 2.0) -> Animation:
    """``LaggedStart`` over the mobjects."""
    return LaggedStart(*(anim(m) for m in mobs), lag_ratio=lag_ratio, run_time=run_time)


def delayed(anim: Animation, start_s: float, total_s: float) -> Animation:
    """Wraps ``anim`` so it runs inside ``[start_s, total_s]`` of one ``play``.

    The result lasts ``total_s``: a wait, then ``anim``, then a wait; a wait with no length
    is left out, since CE rejects a non-positive run time. ValueError when ``anim`` cannot
    finish by ``total_s``.
    """
    start_s = max(start_s, 0.0)
    rest = total_s - start_s - anim.run_time
    # A tolerance, so an exact fit computed in floats (0.1 + 0.2 against 0.3) is not refused
    # and does not leave a wait of 1e-16 s.
    if rest < -CLOCK_EPSILON_S:
        raise ValueError(f"delayed: {anim.run_time} s from {start_s} s ends past total_s {total_s} s")
    # CE manim/animation/composition.py:198-240, manim/animation/animation.py:584-620
    parts = (([Wait(start_s)] if start_s > CLOCK_EPSILON_S else []) + [anim]
             + ([Wait(rest)] if rest > CLOCK_EPSILON_S else []))
    return Succession(*parts)


def question_caption(target: Mobject, text: str) -> VGroup:
    """A caption in the learner's words with an arrow to ``target``, held until the narration answers.

    The caption sits below ``target``, or above it when below would leave the frame; the
    group holds the caption first, then the arrow.
    """
    caption = Text(text, font_size=28, slant=ITALIC).next_to(target, DOWN, buff=0.6)
    if caption.get_bottom()[1] < -FRAME_HEIGHT / 2:
        caption.next_to(target, UP, buff=0.6)
        # CE manim/mobject/geometry/line.py:503
        arrow = Arrow(caption.get_bottom(), target.get_top(), buff=0.1, stroke_width=3)
    else:
        arrow = Arrow(caption.get_top(), target.get_bottom(), buff=0.1, stroke_width=3)
    return VGroup(caption, arrow)
