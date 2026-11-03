# Patterns: the sixteen helpers and the rules they stage

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

This file indexes the sixteen helpers of `scripts/mtv/patterns.py`. The storyboarder chooses
helpers from it and from nowhere else, naming them in each beat's `patterns` field; the
scene coder then reads the docstrings of the helpers its scene names, imports them from
`mtv.patterns` and writes the rest of each beat in plain ManimCE under `manimce.md`. Rule
ids refer to `framework.md`. The index below is generated from `patterns.py` itself (each
helper's signature, the first line of its docstring as its one-line contract, the base class
it needs) and from `PATTERN_TAGS` in `scripts/mtv/common.py`, so where this file and the
code differ, the code is right and this file is out of date.

## What naming a helper does

A beat's `patterns` list does four things and no more.

- `lesson.validate` rejects a value that is not a key of `PATTERN_TAGS`, whose keys are
  exactly the sixteen helpers indexed here.
- The scene coder is given the docstrings of the helpers its beats name, so a helper the
  storyboard leaves out is one the coder has not read.
- `exemplars.py pick --role frame-critic --scene <id>` follows each named helper through
  `PATTERN_TAGS`, and each move through `MOVE_TAGS`, to technique tags, and gives the frame
  critic the most confident pack exemplar of each tag it reaches, at most four. The helpers
  a storyboard names therefore choose what the scene's frames are compared with.
- Through those tags a helper meets the rules: `framework.md` files each rule's examples
  under the tags of its `Exemplars` line. Each index entry lists the rules its tags reach
  and the rules whose text names it, and the table at the end lists them by rule.

Naming a helper satisfies no rule by itself. The `storyboard_check.py` predicates read
`moves`, `introduces`, `shows_value_of`, `symbol_introduced`, the narration and the scene
states, never `patterns`, and the frame critic scores what the frames show. A helper is how
a rule is staged, not evidence that it was.

## Constraints the helpers carry

- Base class. `zoom_to` needs a `NarratedCameraScene` (`scene_kind` `camera`) and
  `orbit_with_hud` a `Narrated3DScene` (`scene_kind` `3d`), and each raises `TypeError` in
  any other scene; the other fourteen work in all three base classes. No scene uses both:
  `check_scenes.py` rejects a class that names `zoom_to` and `orbit_with_hud` together, so a
  lesson that needs a zoom and an orbit gives each its own scene.
- Seed. `LayeredNetwork` takes the lesson's `seed` and draws its weights from it, so a
  re-render gives the same picture. `NumericColumn` and `WeightGrid` take values, not a
  seed: their values come from a `random.Random` seeded with the lesson seed, or from a
  small table of real values typed into the storyboard where that is cheap (R30).
- Colors. `LayeredNetwork` and `WeightGrid` color each weight by its sign through the
  lesson's `weight_pos` and `weight_neg` roles, and `flash_along` lights its path in the
  `emphasis` role unless it is given a color; everything else the helpers draw is white,
  which carries no role. A role missing from the lesson's `colors` falls back to the R19
  palette, so a lesson that uses these helpers keeps those three roles in `colors` with the
  colors it means (R18, R19).
- Numbers. Every number a helper draws is a `DecimalNumber` (`NumericColumn`,
  `count_parameters`, `live_decimal`) and every symbol a `MathTex` (the target of
  `numbers_to_symbol`); `question_caption` draws `Text`, for words. A value the narration
  reads aloud is therefore an object the beat can enlarge or zoom to (R15). `WeightGrid`
  draws no digits: its squares show sign and magnitude as color and opacity, texture under
  R15 unless a `NumericColumn` or a zoom gives the value that matters.
- Crowds. A `LayeredNetwork` layer of more than 16 nodes draws 16 dots with a vertical
  ellipsis between its halves, and `.node(l, i)` indexes the drawn dots. A `LayeredNetwork`
  drawn as one diagram, its long layers cut by their ellipses, and a `WeightGrid` each count
  as one object under R14's budget of 12, as a network drawn as one diagram and a grid do in
  `framework.md`. A full layer stands about 10 units tall at scale 1 against the 8-unit
  frame, so the beat's visual gives the network a scale and a place, and `closing_state`
  records them.

## Choosing a helper

The helpers fall into six groups, the Group of each index entry. Each paragraph names the
rules a helper stages; every link is one `framework.md` makes, through a technique tag or in
the rule's own text.

### Nouns: the recurring cast

`LayeredNetwork`, `NumericColumn` and `WeightGrid` are the objects a lesson about networks
keeps on screen. Give the network one home position in `closing_state` and bring it back
there (R22, `recurring-cast`), and keep it in view, shrunk or dimmed, while one stage is
explained (R21, `pipeline-stays-on-screen`); `.layers`, `.edges` and `.node(l, i)` are the
parts a beat lights, dims or zooms to. A `NumericColumn` is R07's concrete number: the beat
that shows it lists the quantity in `shows_value_of`, and a later beat turns a copy of it
into the symbol. A `WeightGrid` shows many weights at once by sign and magnitude; one cell
worked through before the whole grid follows R05 (`zoom-to-one-unit`).

### Provenance: new objects come from old ones

`provenance` and `numbers_to_symbol` transform a copy, so the source stays where it is while
the new object arrives from it. `numbers_to_symbol` is R07's step: the beat that lists the
symbol in `symbol_introduced` turns the column shown in an earlier beat into it.
`provenance` is R17's: a beat that changes the picture says in its visual which object on
screen becomes which new one. Both default to 2 s, R24's band for a transform that carries
meaning. `save_and_restore_layout` is R23's aside: the beat that opens the aside names in
its visual the group it saves, and when the block closes the group plays back to its saved
state over `run_time`, 1 s by default, so the beat that ends the aside leaves room for that
play. The saved state holds positions, sizes and opacities, so a `focus_and_dim` inside the
block is undone by the same restore, the later beat R12 asks for that brings the dimmed
objects back.

### Emphasis: light, dim, tremble

`focus_and_dim` is R12 and the first half of R05: everything in the group but `keep` fades
to at most `opacity`, 0.2 by default and inside R12's 0.1 to 0.5, and nothing is removed.
`keep` may name a part nested at any depth, such as one node of the network, and the helper
raises `ValueError` when nothing would fade, so `keep` never holds the whole group.
`flash_along` sends a flash along a copy of a path in the emphasis color, R21's way of
lighting the stage being explained while the pipeline stays up (`light-the-path`).
`nudge_and_return` gives one object a 1 s tremor and return, the gesture for asking what
happens if this knob moves; it shares `knobs-tremor` with `live_decimal`, a readout that
follows its tracker. The tag is filed under R26, whose long holds the corpus keeps alive
with small motions like these, but a silent tail of 3 s or more still needs an updater or an
orbit under R26, and a 1 s tremor is neither.

### Numbers: values that change

`live_decimal` binds a `DecimalNumber` to a `ValueTracker` and redraws it every frame, so a
value can run while the rest of the picture holds: R07's number shown before its symbol and,
while an updater drives its tracker, the moving readout that keeps a long hold alive under
R26. `focus_and_dim` leaves updaters running, so a kept live decimal stays live while the
rest dims. `count_parameters` returns a counter, which the scene places and adds, and a 3 s
play in which the counter rises to the network's weight count while the drawn edges brighten
in turn. It counts weights only, each pair of adjacent layers' sizes multiplied and summed
(12960 for 784-16-16-10), so narration that counts biases too names a different number. It
is R07's `parameter-count`, a large count shown before it is named, and R27 puts such a
counting sweep outside both lag bands, since its count sets the pace.

### Camera: the frame as narrator

`zoom_to` animates a camera scene's frame to fit one object with a margin, 2 s by default:
R05's zoom to one unit and R15's enlarged value; a second `zoom_to` on the whole picture
returns from it. `orbit_with_hud` turns a 3D scene's camera through `degrees` over
`run_time`, 60 degrees over 10 s by default and inside R24's 8 to 12 s orbit band, while
`hud` stays fixed in frame. It plays by itself and returns nothing, so the beat calls it
instead of passing it to `self.play`, and the beat needs `run_time` seconds of room. An
orbit is one of the three things that may carry a long hold (R26).

### Narration: timing inside a beat

`staggered` plays one animation per object as a `LaggedStart`, a `FadeIn` at a `lag_ratio`
of 0.5 over 2 s by default. 0.5 is the top of R27's band for a sequential reveal of items
named in turn; for a crowd of n similar items the narration does not name one by one, such
as R05's crowd step after one unit has been worked, the beat asks for a `lag_ratio` near
1/n, 0.05 or less from 20 items on, so the sweep reads as one wave. `delayed` places one
animation inside a longer play, with a wait before it and after it, so a visual lands at its
mark while the play spans the beat (R24's `lands` clause, `micro-timing-in-one-play`); it
raises `ValueError` when the animation cannot finish by `total_s`. `question_caption` draws
a question in the learner's words below its target with an arrow to it, or above when below
would leave the frame, and returns the group for the scene to play in and take away when the
narration answers. It is R03's question planted and held across a beat, set beside its
referent (R13); a question shown only this way does not count toward R09's spoken questions.

## Index

One entry per helper, in the order of `patterns.py`. Signatures are written as `ast.unparse`
gives them; a class's signature is its `__init__` without `self`, returning its base class.
"Rules through its tags" are the rules whose `Exemplars` line names one of the helper's
`PATTERN_TAGS`; "Rules that name it" are the rules whose text mentions the helper.

### `LayeredNetwork`

- Group: nouns
- Signature: `LayeredNetwork(sizes: list[int], seed: int, **kwargs) -> VGroup`
- Methods: `.node(layer: int, index: int) -> Dot`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A layered network with seeded weights colored by sign, `.layers`, `.edges`, `.node(l, i)`.
- Draws text with: `MathTex`
- PATTERN_TAGS: `pipeline-stays-on-screen`, `recurring-cast`
- Rules through its tags: R21, R22
- Rules that name it: R30

### `NumericColumn`

- Group: nouns
- Signature: `NumericColumn(values: list[float], decimals: int=2, **kwargs) -> VGroup`
- Methods: `.at(index: int) -> DecimalNumber`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A vertical column of `DecimalNumber`, `.at(i)`.
- Draws text with: `DecimalNumber`
- PATTERN_TAGS: `numbers-before-symbols`
- Rules through its tags: R07, R11
- Rules that name it: R30

### `WeightGrid`

- Group: nouns
- Signature: `WeightGrid(values: list[float], shape: tuple[int, int], **kwargs) -> VGroup`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A grid of squares filled by sign and magnitude.
- PATTERN_TAGS: `numbers-before-symbols`, `zoom-to-one-unit`
- Rules through its tags: R05, R07, R11, R15
- Rules that name it: R30

### `provenance`

- Group: provenance
- Signature: `provenance(src: Mobject, dst: Mobject, run_time: float=2.0) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: `ReplacementTransform` of a copy of `src` into `dst`, the source stays.
- PATTERN_TAGS: `provenance-transform`, `transitions-reuse-geometry`
- Rules through its tags: R07, R16, R17
- Rules that name it: R17

### `numbers_to_symbol`

- Group: provenance
- Signature: `numbers_to_symbol(column: VGroup, symbol: MathTex, run_time: float=2.0) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: The column's digits collapse into the symbol by transforming copies.
- Draws text with: `MathTex`
- PATTERN_TAGS: `numbers-before-symbols`, `provenance-transform`
- Rules through its tags: R07, R11, R17
- Rules that name it: R17

### `save_and_restore_layout`

- Group: provenance
- Signature: `save_and_restore_layout(scene, group: VGroup, run_time: float=1.0) -> Iterator[None]`
- Decorators: `@contextlib.contextmanager`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: Saves `group` state, yields, restores with `Restore` on exit.
- PATTERN_TAGS: `save-and-restore`
- Rules through its tags: R23
- Rules that name it: R23

### `flash_along`

- Group: emphasis
- Signature: `flash_along(path: VMobject, color=None, time_width: float=1.0) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: `ShowPassingFlash` along a copy of the path.
- PATTERN_TAGS: `light-the-path`, `motion-with-a-reason`
- Rules through its tags: R21, R26
- Rules that name it: R21

### `focus_and_dim`

- Group: emphasis
- Signature: `focus_and_dim(group: VGroup, keep: list[Mobject], opacity: float=0.2) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: Everything in `group` but `keep` fades to `opacity`, nothing is removed.
- PATTERN_TAGS: `dim-not-delete`, `one-then-all`
- Rules through its tags: R05, R12
- Rules that name it: R05, R12

### `nudge_and_return`

- Group: emphasis
- Signature: `nudge_and_return(mob: Mobject, amount: float=0.1) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A small tremor and return, for "what if this knob moves".
- PATTERN_TAGS: `knobs-tremor`
- Rules through its tags: R26
- Rules that name it: none

### `count_parameters`

- Group: numbers
- Signature: `count_parameters(network: LayeredNetwork) -> tuple[DecimalNumber, Animation]`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A counter that increments as edges light up.
- Draws text with: `DecimalNumber`
- PATTERN_TAGS: `parameter-count`, `staggered-reveal`
- Rules through its tags: R07, R25, R27
- Rules that name it: R27

### `live_decimal`

- Group: numbers
- Signature: `live_decimal(tracker: ValueTracker, decimals: int=2) -> DecimalNumber`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: An always-redrawn decimal bound to a tracker.
- Draws text with: `DecimalNumber`
- PATTERN_TAGS: `numbers-before-symbols`, `knobs-tremor`
- Rules through its tags: R07, R11, R26
- Rules that name it: none

### `zoom_to`

- Group: camera
- Signature: `zoom_to(scene: NarratedCameraScene, mob: Mobject, margin: float=0.5, run_time: float=2.0) -> Animation`
- Base class: `NarratedCameraScene` (`scene_kind` `camera`)
- Contract: Frame animates to fit `mob`; requires `NarratedCameraScene`.
- PATTERN_TAGS: `zoom-to-one-unit`, `camera-as-narrator`
- Rules through its tags: R05, R15, R24, R26
- Rules that name it: R05

### `orbit_with_hud`

- Group: camera
- Signature: `orbit_with_hud(scene: Narrated3DScene, hud: VGroup, degrees: float=60.0, run_time: float=10.0) -> None`
- Base class: `Narrated3DScene` (`scene_kind` `3d`)
- Contract: Ambient camera rotation while `hud` stays fixed in frame; requires `Narrated3DScene`.
- PATTERN_TAGS: `camera-as-narrator`, `motion-with-a-reason`
- Rules through its tags: R24, R26
- Rules that name it: none

### `staggered`

- Group: narration
- Signature: `staggered(mobs: Iterable[Mobject], anim=FadeIn, lag_ratio: float=0.5, run_time: float=2.0) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: `LaggedStart` over the mobjects.
- PATTERN_TAGS: `staggered-reveal`, `one-then-all`
- Rules through its tags: R05, R25, R27
- Rules that name it: R05, R27

### `delayed`

- Group: narration
- Signature: `delayed(anim: Animation, start_s: float, total_s: float) -> Animation`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: Wraps `anim` so it runs inside `[start_s, total_s]` of one `play`.
- PATTERN_TAGS: `micro-timing-in-one-play`
- Rules through its tags: R24
- Rules that name it: none

### `question_caption`

- Group: narration
- Signature: `question_caption(target: Mobject, text: str) -> VGroup`
- Base class: any of `NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`
- Contract: A caption in the learner's words with an arrow to `target`, held until the narration answers.
- Draws text with: `Text`
- PATTERN_TAGS: `viewer-voice`, `caption-next-to-referent`
- Rules through its tags: R03, R04, R09, R10, R13
- Rules that name it: R03, R09

## Rules and the helpers that stage them

The same links read by rule, generated from `framework.md` and `PATTERN_TAGS`. "Tags" is the
rule's `Exemplars` line.

| Rule | Tags | Helpers through its tags | Helpers it names |
| --- | --- | --- | --- |
| R01 | `working-thing-first` | none | none |
| R02 | `preview-then-hide` | none | none |
| R03 | `viewer-voice` | `question_caption` | `question_caption` |
| R04 | `caption-next-to-referent` | `question_caption` | none |
| R05 | `zoom-to-one-unit`, `one-then-all` | `WeightGrid`, `focus_and_dim`, `zoom_to`, `staggered` | `focus_and_dim`, `zoom_to`, `staggered` |
| R06 | `carry-picture-forward` | none | none |
| R07 | `numbers-before-symbols`, `provenance-transform`, `parameter-count` | `NumericColumn`, `WeightGrid`, `provenance`, `numbers_to_symbol`, `count_parameters`, `live_decimal` | none |
| R08 | none | none | none |
| R09 | `viewer-voice` | `question_caption` | `question_caption` |
| R10 | `viewer-voice` | `question_caption` | none |
| R11 | `numbers-before-symbols` | `NumericColumn`, `WeightGrid`, `numbers_to_symbol`, `live_decimal` | none |
| R12 | `dim-not-delete` | `focus_and_dim` | `focus_and_dim` |
| R13 | `caption-next-to-referent` | `question_caption` | none |
| R14 | `object-budget`, `montage-scale` | none | none |
| R15 | `zoom-to-one-unit` | `WeightGrid`, `zoom_to` | none |
| R16 | `transitions-reuse-geometry`, `carry-picture-forward` | `provenance` | none |
| R17 | `transitions-reuse-geometry`, `provenance-transform` | `provenance`, `numbers_to_symbol` | `provenance`, `numbers_to_symbol` |
| R18 | `one-color-per-role` | none | none |
| R19 | `one-color-per-role` | none | none |
| R20 | `one-color-per-role` | none | none |
| R21 | `pipeline-stays-on-screen`, `light-the-path` | `LayeredNetwork`, `flash_along` | `flash_along` |
| R22 | `recurring-cast` | `LayeredNetwork` | none |
| R23 | `save-and-restore` | `save_and_restore_layout` | `save_and_restore_layout` |
| R24 | `camera-as-narrator`, `micro-timing-in-one-play` | `zoom_to`, `orbit_with_hud`, `delayed` | none |
| R25 | `staggered-reveal` | `count_parameters`, `staggered` | none |
| R26 | `motion-with-a-reason`, `camera-as-narrator`, `knobs-tremor` | `flash_along`, `nudge_and_return`, `live_decimal`, `zoom_to`, `orbit_with_hud` | none |
| R27 | `staggered-reveal` | `count_parameters`, `staggered` | `count_parameters`, `staggered` |
| R28 | `admit-uncertainty` | none | none |
| R29 | `honest-lie` | none | none |
| R30 | `real-data-where-cheap`, `seeded-randomness` | none | `LayeredNetwork`, `NumericColumn`, `WeightGrid` |

No helper stages R01, R02, R06, R08, R14, R18, R19, R20, R28 or R29: the lesson carries them
in its `colors`, its beats' moves, narration and visual text and its scene states, and the
scene coder in plain ManimCE.
