# ManimCE: translations, checks and timings for the scene coder

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

The scene coder reads this file with its scene of `lesson.json` and the docstrings of the
helpers its beats name. It covers the ManimGL habits, learned from 3Blue1Brown's code, that
fail or change the picture in ManimCE 0.22.0, the version `scripts/requirements.txt` pins,
and the kit's own limits on a scenes file: the ManimGL idioms and their ManimCE
replacements, the 3D camera conversion, the names `check_scenes.py` rejects before a render,
the TeX setup, the base class each camera idiom needs, the run times, waits and lag ratios
the timing rules ask for, the 24 failures `render.py` recognizes in `render.log` with the
fix a retry carries, and why scenes render silent. Rule ids refer to `framework.md`.

The banned-name table and the error table are generated from `BANNED_NAMES` and
`ERROR_TABLE` in `scripts/mtv/common.py`, so where they and the code differ, the code is
right and this file is out of date. Every other statement about ManimCE was checked against
ManimCE 0.22.0, in its source or by building the objects without rendering, except the
caching note at the end, which was measured with renders; every statement about ManimGL was
checked against ManimGL's source.

## ManimGL idioms and their ManimCE replacements

Each row gives a ManimGL idiom, its ManimCE replacement, what differs, and what stops the
idiom when it slips through: `check_scenes.py` before any render, by its lint or by its dry
run, which executes every class's `construct` with the lesson's timings; a row of the error
table, whose pattern names the failure in the dry run's last lines or in `render.log`; or
nothing at all. A row caught by nothing is the dangerous kind: ManimCE renders the scene and
draws a different picture, and only the frame critic can notice. A `TypeError`, `NameError`
or `AttributeError` that no error-table row names fails the dry run, and the re-dispatch
carries the dry run's last lines instead of a fix text. Names in the banned-name table are
repeated here only where something beyond the name needs saying.

### Scenes and the camera

| ManimGL | ManimCE | Note | Caught by |
| --- | --- | --- | --- |
| `from manimlib import *` | nothing in the class: the parent's shared header of `lesson.py` already holds `from manim import *`, the `mtv.narrated` bases and `from mtv.patterns import *` | | banned `manimlib` |
| a scene class based on `InteractiveScene`, `Scene` or `ThreeDScene` | `NarratedScene`, `NarratedCameraScene` or `Narrated3DScene`, the base its `scene_kind` names | only the narrated bases time the beats and write the run log | banned `InteractiveScene`; `check_scenes.py` (base against `scene_kind`) |
| `CONFIG = {...}` | class attributes or `__init__` keyword arguments | | banned `CONFIG` |
| `self.frame.animate.move_to(p).set_height(h)`, a flat pan or zoom | `zoom_to(self, mob)`, or `self.camera.frame.animate.move_to(p).set(height=h)`, in a `NarratedCameraScene` | `reorient(0, 0, 0, center, height)` is the same flat move and needs no 3D scene | `check_scenes.py` (`self.frame`); error-table row 10 when the CE form runs in a scene without a camera frame |
| `self.frame.save_state()`, then `Restore(self.frame)` | `self.camera.frame.save_state()`, then `Restore(self.camera.frame)`, in a `NarratedCameraScene` | the moving camera's frame saves and restores like any mobject (R23) | `check_scenes.py` (`self.frame`) |
| `frame.reorient(theta, phi, gamma, center, height)` | `self.set_camera_orientation(...)` for a cut, `self.move_camera(...)` for a move, in a `Narrated3DScene` | the angles convert by fixed rules: see the next section | banned `reorient` |
| `frame.add_ambient_rotation(rate)` | `orbit_with_hud(self, hud, degrees, run_time)`, which runs `begin_ambient_camera_rotation` | | `check_scenes.py` (`self.frame`) |
| `mob.fix_in_frame()` | `self.add_fixed_in_frame_mobjects(mob)` in a `Narrated3DScene`; `orbit_with_hud` fixes its `hud` itself | | banned `fix_in_frame` |
| a label that must keep facing the viewer in 3D | `self.add_fixed_orientation_mobjects(label)` | the label still moves with the scene; only its orientation is fixed | none |
| `self.set_floor_plane("xz")` | none; build the content with z up | see the next section | banned `set_floor_plane` |
| `frame.set_field_of_view(f)` | `focal_distance=h / (2 * np.tan(f / 2))` in `set_camera_orientation` or `move_camera`, `h` being the ManimGL frame height | `from manim import *` exports `np`, not `math` | `check_scenes.py` (`self.frame`) |
| `FRAME_WIDTH`, `FRAME_HEIGHT`, `FRAME_X_RADIUS` | `config.frame_width` (14.22), `config.frame_height` (8.0), `config.frame_x_radius` | `from manim import *` exports none of these names | `check_scenes.py`'s dry run: a `NameError`, which no error-table row names |
| a `random_seed` class attribute, or `random` and `numpy.random` left unseeded | the lesson's `seed`, which the parent's shared header defines as `SEED`: `LayeredNetwork(sizes, seed=SEED)`, and `random.Random(SEED)` for every other value (R30) | CE seeds from `Scene`'s `random_seed` constructor argument, or else from `config.seed`, which the kit's `manim.cfg` leaves unset; `__init__` overwrites a `random_seed` class attribute with that value, so the attribute seeds nothing | none: each render draws a different picture |

### Text and TeX

| ManimGL | ManimCE | Note | Caught by |
| --- | --- | --- | --- |
| ManimGL `Tex(r"a^2 + b^2")`, which is math mode | `MathTex(r"a^2 + b^2")` | CE's `Tex` is text mode, so math ported unchanged stops LaTeX with `Missing $ inserted` | error-table row 12 |
| `TexText("words")` | `Tex("words")` | | banned `TexText` |
| `TexMobject`, `TextMobject` (2017 code) | `MathTex`, `Tex` | | banned `TexMobject`, `TextMobject` |
| `OldTex`, `OldTexText` | `MathTex`, `Tex`, each part a separate argument | | banned `OldTex`, `OldTexText` |
| `tex["x"]`, `text["word"]`: a part picked by its string | `MathTex(..., substrings_to_isolate=["x"])` and `get_part_by_tex("x")`, or `{{ x }}` groups; for `Text`, `t2c={...}` or one `Text` per word | CE's `Text` keeps no glyph for a space, so a slice counts letters only | `check_scenes.py`'s dry run: a `TypeError` (`range indices must be integers or slices, not str`), which no error-table row names |
| `isolate=[...]` | `substrings_to_isolate=[...]` | | banned `isolate` |
| `TransformMatchingStrings` | `TransformMatchingTex` between `MathTex` with isolated parts, `TransformMatchingShapes` between `Text` | | `check_scenes.py`'s dry run: a `NameError`, which no error-table row names |
| `Text("a\nb", alignment="LEFT")` | `Paragraph("a", "b", alignment="left")` | | `check_scenes.py`'s dry run: a `TypeError` (`unexpected keyword argument 'alignment'`), which no error-table row names |
| `Text(..., font="...")` | leave the font out | `look.apply` sets `Text`'s default font from `look.pick_font()` | error-table row 14, a warning that never fails a render |

### Animations and waits

| ManimGL | ManimCE | Note | Caught by |
| --- | --- | --- | --- |
| `ShowCreation(m)` | `Create(m)` | | banned `ShowCreation` |
| `ShowCreationThenDestruction(m)` | `flash_along(m)`, or `ShowPassingFlash(m.copy(), time_width=...)` | ManimGL's default `time_width` is 2.0, `flash_along`'s 1.0 and CE `ShowPassingFlash`'s 0.1: choose the streak length the beat needs | banned `ShowCreationThenDestruction` |
| `FlashAround(m)` | `Circumscribe(m)` | CE's `Circumscribe` defaults to `time_width=0.3` and `fade_out=False` | banned `FlashAround` |
| `FadeIn(m, UP)`, the shift passed by position | `FadeIn(m, shift=UP)` | CE reads a second positional argument as another mobject | `check_scenes.py`'s dry run: a `TypeError` (`Only values of type Mobject can be added as submobjects of Group`), which no error-table row names |
| `self.play(m.shift, UP)`: a bound method passed to `play` (2017 code; ManimGL plays it as a `MoveToTarget`) | `self.play(m.animate.shift(UP))`; several methods chain on one `.animate` | | `check_scenes.py` (`play(mob.method)`); error-table row 1 |
| `self.play(m.restore)` | `self.play(Restore(m))` after `m.save_state()`, or `with save_and_restore_layout(self, group):` | | `check_scenes.py` (`play(mob.method)`); error-table row 1; error-table row 4 when the port plays `Restore(m)` without `m.save_state()` |
| `ApplyMethod(m.method, *args, path_arc=a)` | `m.animate(path_arc=a).method(*args)` | `ApplyMethod` still exists in CE 0.22.0; `.animate` is the CE idiom | none |
| `m.animate.method(...).set_anim_args(run_time=2)` | `m.animate(run_time=2).method(...)` | CE takes animation arguments before the method; row 8 is the other wrong order | `check_scenes.py`'s dry run: a `TypeError` (`setter() got an unexpected keyword argument 'run_time'`), which no error-table row names |
| `time_span=(a, b)` on an animation inside a `play` | `delayed(anim, a, total_s)` | | banned `time_span` |
| `LaggedStart(..., group_type=Group)` | the same call without `group_type` | | `check_scenes.py`'s dry run: a `TypeError` (`unexpected keyword argument 'group_type'`), which no error-table row names |
| `Transform(a, b).update(1)`, an instant snap | `a.become(b)` | | `check_scenes.py`'s dry run: an `AttributeError` (`'Transform' object has no attribute 'update'`), which no error-table row names |
| `m.animate.fade(x)` | unchanged, or `focus_and_dim(group, keep, opacity)` when faint parts must stay faint | for a VMobject both libraries multiply each part's fill and stroke opacity by 1 - x: ManimGL's `VMobject.fade` overrides `Mobject.fade`, whose outright 1 - x reaches only non-vector mobjects; so a second fade compounds in both, and `set_opacity(o)` would set every part to o and raise a faint fill (R12) | nothing to catch |
| `VGroup(generator)`, `LaggedStart(generator)` | unchanged | CE 0.22.0 accepts an iterable here; unpacking with `*` works too | nothing to catch |
| bare `self.wait()` | `self.wait()`, which is 1.0 s in both libraries | inside a beat, take waits from `b.until(mark)` and end on `self.wait(b.remaining())` | error-table row 3 for a computed wait at or below 0 |

### Mobjects and colors

| ManimGL | ManimCE | Note | Caught by |
| --- | --- | --- | --- |
| ManimGL `YELLOW` (`#FFFF00`) | `PURE_YELLOW` | CE's `YELLOW` is `#F7D96F`; of the 56 color names both libraries define, only `YELLOW_C` (so `YELLOW`) and `BLUE_E` (`#1C758A` in ManimGL, `#236B8E` in CE) differ | `check_scenes.py` (a color outside the lesson's `colors` and the neutrals) |
| `SurroundingRectangle(m)` in its default color | `SurroundingRectangle(m, color=...)` with the lesson's `emphasis` color | both libraries default to `#FFFF00`; naming the color keeps the role in the code (R18) | none |
| `FullScreenRectangle()` | `FullScreenRectangle(fill_color=BLACK, fill_opacity=0.7, stroke_width=0)` for a dimming overlay | ManimGL's is filled `GREY_E` at opacity 1 with no stroke, CE's is unfilled with a white stroke of width 4; no grey card is used (R20) | none: a white outline appears instead of a card |
| `NumberLine((0, 10, 1), width=6)`, `Axes((0, 10, 1), (0, 5, 1), width=6, height=4)` | `NumberLine(x_range=[0, 10, 1], length=6)`, `Axes(x_range=[0, 10, 1], y_range=[0, 5, 1], x_length=6, y_length=4)` | | `check_scenes.py`'s dry run: a `TypeError` (`unexpected keyword argument 'width'`), which no error-table row names |
| pi creatures, `TeacherStudentsScene`, speech and thought bubbles | `question_caption(target, text)` for a question in the learner's words, or no character at all | 3Blue1Brown's characters are not copied | banned `PiCreature`, `SpeechBubble`, `ThoughtBubble`; `check_scenes.py` (base against `scene_kind`) |
| a helper from the 3b1b/videos repository (a matrix of decimals, context arcs, a digit image) | CE primitives (`DecimalMatrix`, `ShowPassingFlash` over arcs) or the kit's helpers | such helpers belong to neither library | `check_scenes.py`'s dry run: a `NameError`, which no error-table row names |
| `ImageMobject`, a file read, a URL | seeded synthetic values drawn as vector mobjects (R30) | | banned `ImageMobject`, `open`, `Path`, `requests`, `urllib` |
| `apply_depth_test()`, `set_shading(...)`, `set_flat_stroke(...)` | leave them out; order overlapping objects with `set_z_index` | Cairo has no depth test or shading switch; `set_flat_stroke(False)` passes silently and does nothing | `check_scenes.py`'s dry run: an `AttributeError` or a `TypeError`, which no error-table row names |

## The 3D camera: `reorient` and `set_camera_orientation`

ManimGL's camera frame takes `reorient(theta, phi, gamma, center, height)` in degrees.
ManimCE's `ThreeDScene`, and so `Narrated3DScene`, takes `set_camera_orientation(phi, theta,
gamma, zoom, focal_distance, frame_center)` in radians, and `move_camera` with the same
arguments plus `added_anims`. Beyond degrees to radians the conversion follows fixed rules.
They were derived from the two libraries' camera code, ManimGL's `CameraFrame` and ManimCE
0.22.0's `three_d_camera.py`, and checked by projecting random points through both cameras:
over 200 random poses on each floor plane, the projections agree to within 3e-14 of a frame
unit, an eighth of the frame's height. No render was made for the check. ManimGL's
`CameraFrame` is in `camera/camera.py` at v1.6.1 and in `camera/camera_frame.py` from
January 2023, v1.7 included. Its Euler-angle convention is the same from v1.6.1 on, while
the 45-degree field of view (January 2023; v1.6.1 puts the focal distance at twice the frame
height) and `reorient`'s `center` and `height` arguments (February 2024) came later, before
the code of the 2024 lessons, which the table below follows.

| ManimGL `reorient` | ManimCE `set_camera_orientation` or `move_camera` |
| --- | --- |
| `phi` (degrees) | `phi=phi * DEGREES` |
| `theta` (degrees) | `theta=(theta - 90) * DEGREES` |
| `gamma` (degrees) | `gamma=-gamma * DEGREES` |
| `center` | `frame_center=center` |
| `height` | `zoom=config.frame_height / height`, that is `8 / height` |
| the field of view, 45 degrees unless `set_field_of_view` changed it | `focal_distance=height / (2 * np.tan(fov / 2))`, about `1.207 * height` at 45 degrees |

- Theta shifts by 90 degrees because CE's head-on view is `theta=-90 * DEGREES` where
  ManimGL's is theta 0, so `reorient(0, 0, 0)` is CE's default view, `phi=0, theta=-90 *
  DEGREES, gamma=0`.
- Gamma, the roll, changes sign. Every `reorient` call the corpus records quote with numbers
  sets gamma to 0, so the corpus never shows the difference.
- CE keeps `focal_distance` at 20 whatever the zoom, while ManimGL's is 1.207 times the
  frame height (9.66 at the default height 8), so the same pose looks flatter in CE unless
  `focal_distance` is passed.
- A bare `frame.reorient(...)` is a cut: `self.set_camera_orientation(...)`.
  `frame.animate.reorient(...)`, or `MoveToTarget(frame)` inside a `play`, is a move:
  `self.move_camera(..., added_anims=[...], run_time=...)`. `move_camera` calls `play`
  itself, so the beat's other animations ride in `added_anims` and its `run_time` stretches
  them all; an animation that must keep its own length goes in as `delayed(anim, start_s,
  total_s)` with `total_s` equal to the move's `run_time`.
- An angle left out keeps its current value in both libraries. The end pose of a move
  matches; the path to it may not, because ManimGL blends the frame's whole orientation
  while CE moves each angle on its own tracker.
- All three angles zero is a flat pan and zoom. `reorient(0, 0, 0, center, height)` becomes
  `self.camera.frame.animate.move_to(center).set(height=height)` in a `NarratedCameraScene`,
  or `zoom_to`, and needs no 3D scene; many of the corpus's `reorient` calls are of this
  kind (attention s22, s26, s34, s35; mlp s10, s12, s14, s15, s16, s21).

ManimGL's `set_floor_plane("xz")` makes y the up axis and turns theta about it. ManimCE has
no such switch, and the rules above, applied to an xz-floor pose, draw points far from where
ManimGL draws them: at the default height 8, the point within 2 units of the center that
misses most is about 3 frame units off at a typical pose and up to 4 over 200 random poses.
Build the content with z up instead: rotate it by +90 degrees about `RIGHT`
(`group.rotate(90 * DEGREES, axis=RIGHT, about_point=ORIGIN)`, which sends a ManimGL point
(x, y, z) to (x, -z, y)), send `center` through the same rotation, and use phi + 90, theta -
90 and -gamma, each in degrees times `DEGREES`. Content left unrotated needs a full Euler
decomposition per pose; its one short case is a sideways swing, ManimGL theta t with phi and
gamma 0, which is CE `phi=t * DEGREES, theta=0, gamma=90 * DEGREES`.

The two conventions differ beyond degrees to radians: theta moves by 90 degrees, gamma
changes sign, height becomes zoom, the perspective differs and the xz floor has no
counterpart. The analysis records disagreed (attention s05 against s31), and both scenes
stand on an xz floor, s05's inherited from its parent class. s05 kept phi and subtracted 90
from theta, the xy rule, which at that scene's first pose, height 5.28, draws points within
2 units of its center up to about 2.5 frame units off; s31 put the turn into phi with theta
0 and gamma 90, which is exact for a pure sideways swing, phi taking ManimGL's theta with
the same sign, and at that scene's pose, a 7-degree tilt at height 20, up to about 0.1 frame
units off. Rotating the content and applying the xz rule above is exact for both.

```python
# ManimGL, xy floor: frame.reorient(-30, 70, 0, ORIGIN, 6)
self.set_camera_orientation(
    phi=70 * DEGREES, theta=-120 * DEGREES, gamma=0, zoom=8 / 6, frame_center=ORIGIN
)

# ManimGL, xz floor: frame.reorient(20, 15, 0, (1, 2, 0), 8)
stack.rotate(90 * DEGREES, axis=RIGHT, about_point=ORIGIN)  # z up; (1, 2, 0) becomes (1, 0, 2)
self.set_camera_orientation(
    phi=105 * DEGREES, theta=-70 * DEGREES, gamma=0, zoom=1, frame_center=[1, 0, 2]
)
```

## Names `check_scenes.py` rejects

`check_scenes.py` parses `lesson.py` before any render and rejects every use of a name
below, whether called, read as an attribute, passed as a keyword or imported; the finding's
`fix` is the right-hand column. The list holds the ManimGL names that ManimCE 0.22.0 lacks
or keeps only for its OpenGL renderer and interactive use (`get_width` and `set_height`
still exist in CE and are banned all the same), and the names through which a scene could
read a file or reach the network, since a render loads no raster image, downloads nothing
and reaches its lesson only through `load_lesson`.

Beyond names, the same check rejects `self.frame` (fix: `self.camera.frame` in a
`NarratedCameraScene`); a `play` given a bound method, `self.play(mob.method)` (fix:
`self.play(mob.animate.method(...))`); a color constant that is neither a value of the
lesson's `colors` nor a neutral, `WHITE`, `BLACK` or a grey (R18, R19); a scene class
missing from the file or on a base its `scene_kind` does not name; and a class that names
both `zoom_to` and `orbit_with_hud` (fix: one camera idiom per scene).

| Name | Fix the finding carries |
| --- | --- |
| `manimlib` | `from manim import *` |
| `ImageMobject` | `vector mobjects; a render loads no raster image` |
| `open` | `self.load_lesson(scene_id), which finds lesson.json through MTV_LESSON` |
| `Path` | `self.load_lesson(scene_id), which finds lesson.json through MTV_LESSON` |
| `requests` | `values computed in the scene; a render has no network access` |
| `urllib` | `values computed in the scene; a render has no network access` |
| `InteractiveScene` | `NarratedScene, NarratedCameraScene or Narrated3DScene, as scene_kind says` |
| `CONFIG` | `class attributes or __init__ keyword arguments` |
| `TexMobject` | `MathTex` |
| `TextMobject` | `Tex` |
| `TexText` | `Tex` |
| `OldTex` | `MathTex("a", "+", "b", arg_separator=" ")` |
| `OldTexText` | `Tex("word", "word", arg_separator="")` |
| `ShowCreation` | `Create` |
| `ShowCreationThenDestruction` | `ShowPassingFlash(m, time_width=1.0)` |
| `ShowCreationThenFadeOut` | `Succession(Create(m), FadeOut(m))` |
| `ShowCreationThenDestructionAround` | `Circumscribe(m)` |
| `ShowPassingFlashAround` | `Circumscribe(m)` |
| `FlashAround` | `Circumscribe(m)` |
| `FlashUnder` | `ShowPassingFlash(Underline(m), time_width=1.0)` |
| `CircleIndicate` | `Circumscribe(m, shape=Circle)` |
| `VShowPassingFlash` | `ShowPassingFlash(m, time_width=0.1)` |
| `VFadeIn` | `FadeIn` |
| `VFadeOut` | `FadeOut` |
| `VFadeInThenOut` | `Succession(FadeIn(m), FadeOut(m))` |
| `FadeInFromPoint` | `FadeIn(m, target_position=point, scale=0.1)` |
| `FadeOutToPoint` | `FadeOut(m, target_position=point, scale=0.1)` |
| `WiggleOutThenIn` | `Wiggle(m)` |
| `CountInFrom` | `num.set_value(source), then ChangeDecimalToValue(num, target)` |
| `TurnInsideOut` | `none in ManimCE; Transform(m, target) or FadeIn(m)` |
| `FlashyFadeIn` | `none in ManimCE; FadeIn(m)` |
| `TexMatrix` | `Matrix` |
| `GlowDot` | `Dot inside concentric Circles of decreasing fill opacity` |
| `GlowDots` | `VGroup of Dot` |
| `DotCloud` | `VGroup of Dot` |
| `TrueDot` | `Dot` |
| `Checkmark` | `Tex(r"\checkmark")` |
| `Exmark` | `MathTex(r"\times")` |
| `PiCreature` | `none in ManimCE, and 3b1b's drawings are not copied; leave the character out` |
| `SpeechBubble` | `question_caption(target, text)` |
| `ThoughtBubble` | `question_caption(target, text)` |
| `TexturedSurface` | `Surface with fill_color or checkerboard_colors; a render loads no texture image` |
| `ParametricSurface` | `Surface(func, u_range, v_range, resolution)` |
| `Square3D` | `Square().set_shade_in_3d()` |
| `VCube` | `Cube(side_length, fill_opacity)` |
| `VPrism` | `Prism` |
| `FullScreenFadeRectangle` | `FullScreenRectangle(fill_color=BLACK, fill_opacity=0.7, stroke_width=0)` |
| `set_backstroke` | `set_stroke(BLACK, width, background=True)` |
| `get_grid` | `arrange_in_grid(rows, cols) on a VGroup of copies` |
| `replicate` | `VGroup(*(mob.copy() for _ in range(n)))` |
| `fix_in_frame` | `self.add_fixed_in_frame_mobjects(mob) in a Narrated3DScene` |
| `set_max_width` | `if mob.width > w: mob.scale_to_fit_width(w)` |
| `set_max_height` | `if mob.height > h: mob.scale_to_fit_height(h)` |
| `set_min_width` | `if mob.width < w: mob.scale_to_fit_width(w)` |
| `reorient` | `self.set_camera_orientation or self.move_camera, in radians, in a Narrated3DScene` |
| `set_height` | `mob.scale_to_fit_height(h), or mob.height = h` |
| `set_width` | `mob.scale_to_fit_width(w), or mob.width = w` |
| `get_width` | `mob.width` |
| `get_height` | `mob.height` |
| `make_number_changeable` | `a DecimalNumber or live_decimal(tracker) placed with move_to(part)` |
| `select_part` | `tex.get_part_by_tex("x") on an isolated substring` |
| `select_parts` | `tex.get_part_by_tex("x") on an isolated substring` |
| `add_coordinate_labels` | `add_coordinates()` |
| `get_graph` | `axes.plot(f, x_range=...)` |
| `get_v_line_to_graph` | `axes.get_vertical_line(axes.i2gp(x, graph))` |
| `get_area_under_graph` | `axes.get_area(graph, x_range=...)` |
| `set_floor_plane` | `none in ManimCE; drop the call` |
| `embed` | `none in a ManimCE render; drop the call` |
| `checkpoint_paste` | `none in ManimCE; drop the call` |
| `time_span` | `delayed(anim, start_s, total_s), or rate_func=squish_rate_func(smooth, a / T, b / T) with run_time=T` |
| `isolate` | `substrings_to_isolate=[...] on MathTex, or {{ x }} groups` |

## TeX

- `look.apply`, which `load_lesson` runs in every scene, sets `config.tex_template` to
  `TexTemplateLibrary.threeb1b` plus one macro, `\minus`, a typographic minus; both
  `manim.cfg` files leave `tex_template` empty on purpose. Write formulas for that template
  and no other: no `tex_template=` argument and no preamble in a scene, and a package a
  formula needs is added in `look.py` only (error-table row 12).
- In ManimCE 0.22.0, `TexTemplateLibrary.default` and `TexTemplateLibrary.threeb1b` are
  built from the same preamble. `TexTemplate()` with no arguments, which is what an empty
  `tex_template` key leaves in force when nothing sets a template in code, holds three
  packages: `babel` (english), `amsmath` and `amssymb`.
- Beyond those three, `threeb1b` loads `calligra`, `tipa`, `wasysym`, `dsfont`, `physics`
  and `mathrsfs`, with `inputenc`, `fontenc`, `lmodern`, `setspace`, `relsize`, `textcomp`,
  `ragged2e`, `xcolor` and `microtype`. On Ubuntu 24.04 `dsfont` comes from
  `texlive-fonts-extra`, `physics` from `texlive-science`, `calligra` and `relsize` from
  `texlive-latex-extra`, `wasysym` from `texlive-fonts-recommended`, `tipa` from the `tipa`
  package that `texlive-fonts-recommended` recommends, and `mathrsfs` from
  `texlive-latex-recommended`. `preflight.py` prints the line that installs them all:
  `apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended
  texlive-fonts-extra texlive-science dvisvgm`.
- `physics` makes `\div` its divergence; `look.py` restores ÷, and `\divergence` keeps ∇·.
- LaTeX missing stops the run before any scene renders; a formula never falls back to
  `Text`.
- `MathTex` is math mode and `Tex` text mode. Give a part you will color, move or transform
  its own argument, or name it in `substrings_to_isolate`, so `get_part_by_tex` and
  `TransformMatchingTex` can find it.

## Base classes and camera idioms

| `scene_kind` | Base class | Camera idioms it allows |
| --- | --- | --- |
| `flat` | `NarratedScene` | none; the frame stays put |
| `camera` | `NarratedCameraScene` | `zoom_to`; `self.camera.frame.animate` pans and zooms; `save_state` and `Restore` on the frame |
| `3d` | `Narrated3DScene` | `orbit_with_hud`; `set_camera_orientation`; `move_camera`; `add_fixed_in_frame_mobjects`; `add_fixed_orientation_mobjects` |

- `zoom_to` needs a `NarratedCameraScene` and `orbit_with_hud` a `Narrated3DScene`; each
  raises `TypeError` in any other scene. No scene does both: `check_scenes.py` rejects a
  class that names `zoom_to` and `orbit_with_hud` together, so a lesson that zooms and
  orbits gives each its own scene.
- `zoom_to(scene, mob)` animates the frame over 2 s to fit `mob` with a margin of 0.5 on
  every side, keeping the frame's aspect ratio. The frame a camera scene shows at each
  beat's exit is written to the run log, and the clipped-object check reads boxes against
  it.
- `orbit_with_hud(scene, hud)` fixes `hud` in the frame, turns the camera 60 degrees over 10
  s by default and plays that wait itself, so call it inside a beat whose narration has room
  for its `run_time`.
- A 3D scene's run log holds no camera frame, and its boxes are the objects' scene-unit
  extents, not projected through the turned or zoomed camera, so the frame critic judges a
  3D scene's clipping from its frames alone; keep its objects inside the frame at every
  angle the camera passes through.
- A plain scene's camera has no frame (error-table row 10), and a 3D scene's camera moves
  only through the `ThreeDScene` methods in the table.

## Run times, waits and lag ratios

No gate reads these numbers: `check_scenes.py` checks names, not literals, and the frame
critic scores the pacing under the rubric's motion item from the six-frame sheet. The
storyboard's `visual` says what kind each play is; turn the kind into the literal below.

| The storyboard says | Literal | Rule |
| --- | --- | --- |
| a confirmation: a check, a highlight, a label settling | `run_time=1` | R24 |
| a transform that carries meaning | `run_time=2` | R24 |
| a reveal of several parts | `run_time` from 3 to 5 | R24 |
| a camera orbit (3D scenes only) | 8 to 12 s: `orbit_with_hud(self, hud, run_time=10)` | R24 |
| after most plays | `self.wait(1)` | R25 |
| at the close of a step | `self.wait(2)` | R25 |
| a hold of 3 s or more | only under narration, a running updater or an orbit | R26 |
| a crowd of n similar items, not named one by one | `lag_ratio` near `1 / n`, 0.05 or less from 20 items on (the corpus crowds run 0.001 to 0.05) | R27 |
| a sequential reveal of items named in turn | `lag_ratio` from 0.1 to 0.5 (`staggered` defaults to 0.5) | R27 |

Inside a beat the narration sets the clock, and it wins over the bands. A play that lands a
`lands` visual ends at its mark: wait out the lead-in, then play for `b.until(mark)`, which
by then is about the band. When the mark comes sooner than the band allows, `b.until(mark)`
is shorter and the landing still holds, which is the sync half of R24. The beat ends on
`self.wait(b.remaining())`, and a wait from the table that would run past the narration is
shortened, not kept.

```python
with self.beat("s02-b03") as b:
    lead_in = b.until("sum") - 2.0  # a transform that carries meaning: 2 s
    if lead_in > 0:
        self.wait(lead_in)
    self.play(numbers_to_symbol(column, symbol, run_time=b.until("sum")))
    self.wait(b.remaining())
```

ManimCE's `LaggedStart` gives each of n equal animations T / (1 + r(n - 1)) seconds of a
T-second play at lag ratio r. At r = 1 / n each item animates for about half the play while
the starts spread over the other half, so the crowd reads as one wave; at r = 0.5 each cell
of a 784-cell grid gets about 5 ms of a 2 s play and blinks on. A lag ratio from 2017 code
is never copied: before ManimGL's February 2019 rewrite, which ManimCE follows, a
`LaggedStart` `lag_ratio` was each item's share of the play, so 0.2 to 0.8 meant overlapping
waves, and a lagged start over a group's parts ran each part for half the play, about 1 / n
today; the 0.5 that such code now passes in its place is a later substitution, which blinks
the 784-cell grid on as above. Past 0.5 each item is mostly done before the next starts, so
play such steps as separate plays with the waits above.

## The error table

When a render fails, `render.py` matches `render.log` against the patterns below in order,
after dropping log records below ERROR and the source lines Rich prints around each
traceback frame; the first match names the row, and the owning coder retries with that row's
fix text, three attempts per scene. The table is generated from `ERROR_TABLE` in
`scripts/mtv/common.py`. Row 14 matches a warning, which never fails a render, and ManimCE
prints nothing for row 15's symptom; `render.py` writes row 16's line itself, and row 24's
message comes from `pip`, never from `render.log`. Those rows serve this table and the retry
prompt.

| Row | Pattern searched in `render.log` | Cause (usually a ManimGL habit) | ManimCE replacement | Fix text the retry carries |
| --- | --- | --- | --- | --- |
| 1 | `Passing Mobject methods to Scene\.play` | `self.play(mob.shift, UP)` | `self.play(mob.animate.shift(UP))` | Animate the method through .animate, as in self.play(mob.animate.shift(UP)), instead of passing the bound method and its arguments to play. |
| 2 | `Called Scene\.play with no animations` | `self.play(*[])` | `guard empty lists before play` | Guard empty lists before play, so a call whose unpacked animation list comes out empty is skipped. |
| 3 | `has a (total run_time\|duration\|max_time) of .* <= 0 seconds\|run_time of .* cannot be negative` | `a run_time computed from audio came out non-positive` | `b.until(mark) and b.remaining(), which clamp to one frame` | Take every run_time and wait duration inside a beat from b.until(mark) or b.remaining(), which clamp to one frame, instead of computing it from the audio. |
| 4 | `Trying to restore without having saved` | `Restore(m) without m.save_state()` | `save_and_restore_layout(scene, group)` | Make the change inside save_and_restore_layout(scene, group), the context manager that saves the group's state before it restores it, instead of a bare Restore(m). |
| 5 | `MoveToTarget called on mobject.*'target'\|get_point_mobject not implemented for Mobject\b` | `MoveToTarget(m) without generate_target()` | `call m.generate_target(), mutate m.target, then MoveToTarget(m)` | Call m.generate_target(), mutate m.target, then play MoveToTarget(m). |
| 6 | `You can try adding this value into a Group instead` | `a non-VMobject inside VGroup` | `Group(...)` | Collect the members in Group(...), since a VGroup accepts only VMobject members. |
| 7 | `Animation only works on Mobjects\|cannot be converted to an animation` | `a list of animations passed unexpanded` | `unpack with *` | Unpack the list of animations with \*, as in self.play(\*anims), so play receives animations, not a list. |
| 8 | `Animation arguments must be passed before accessing methods` | `mob.animate.shift(UP)(run_time=2)` | `mob.animate(run_time=2).shift(UP)` | Pass animation arguments to animate before the method, as in mob.animate(run_time=2).shift(UP). |
| 9 | `Method chaining is currently not supported for overridden animations` | `chaining after an overridden animate method` | `separate play calls` | Split the chain into separate play calls, one for each overridden animate method. |
| 10 | `object has no attribute 'frame'` | `self.camera.frame in a plain Scene` | `NarratedCameraScene and zoom_to` | Subclass NarratedCameraScene and move the camera with zoom_to, because a plain scene's camera has no frame. |
| 11 | `has no attribute '(set_backstroke\|get_grid\|replicate\|fix_in_frame\|set_max_width\|reorient\|set_height\|set_width)'` | `a GL-only method` | `the translation rows: set_stroke(BLACK, w, background=True), arrange_in_grid, VGroup(*(m.copy() ...)), add_fixed_in_frame_mobjects, scale_to_fit_width, set_camera_orientation, mob.height = h, mob.width = w` | Replace the GL-only method by its translation row: set_stroke(BLACK, w, background=True) for set_backstroke, arrange_in_grid for get_grid, VGroup(\*(m.copy() ...)) for replicate, add_fixed_in_frame_mobjects for fix_in_frame, scale_to_fit_width for set_max_width, set_camera_orientation for reorient, and mob.height = h or mob.width = w for set_height or set_width. |
| 12 | `latex\ error\ converting\ to` | `LaTeX absent, a missing package or a bad formula` | `fix the formula; a missing package is added only in look.py` | Fix the formula, and when the log names a missing LaTeX package, add it only in look.py, never in a scene. |
| 13 | `dvisvgm.*(not found\|at least version 2\.4)` | `dvisvgm missing or older than 2.4` | `install the dvisvgm system package, 2.4 or newer` | Install the dvisvgm system package, version 2.4 or newer, then rerun preflight.py before rendering again. |
| 14 | `Font .* not in \[` | `a font Pango does not have` | `look.pick_font() chooses from FONT_CANDIDATES` | Take the font from look.pick_font(), which chooses an installed one from FONT_CANDIDATES, instead of naming a font. |
| 15 | `updaters? (do\|did) nothing\|updater (never\|not) (ran\|called)` | `a mobject or tracker never added to the scene` | `self.add(tracker, mob); live_decimal` | Add the tracker and the mobject with self.add(tracker, mob) before animating the tracker, or show a tracked value with live_decimal. |
| 16 | `beat .* missing from the section index` | `a section with no play or wait` | `b.remaining() inside the beat; the mixin's exit pad` | Give the beat a play or a self.wait(b.remaining()) inside its with block, so its section holds frames, and let the mixin's exit pad finish it. |
| 17 | `--output_file can only be used when rendering exactly one scene` | `-o with several scenes` | `rely on default names` | Drop -o and rely on default names, since each scene renders in its own process. |
| 18 | `--format=webm for transparent video` | `-t with MP4` | `never -t; MP4 only` | Never pass -t, since renders are MP4 only and MP4 has no alpha channel. |
| 19 | `There are no scenes inside that module\|is not in the script` | `the class is missing or construct is misspelled` | `define scene_class exactly as lesson.json names it` | Define scene_class exactly as lesson.json names it, with its method spelled construct. |
| 20 | `Too few rows and columns to fit all` | `arrange_in_grid(rows, cols) too small` | `fix the counts` | Fix the counts so that rows times cols in arrange_in_grid covers every submobject. |
| 21 | `Alpha .* not between 0 and 1` | `point_from_proportion out of range` | `clamp alpha` | Clamp alpha to the range 0 to 1 before passing it to point_from_proportion. |
| 22 | `A static Wait animation cannot have a stop condition` | `wait(stop_condition=..., frozen_frame=True)` | `drop one of them` | Drop one of them, since a wait takes stop_condition or frozen_frame=True but not both. |
| 23 | `Expected all inputs for parameter mobjects to be a Mobjects` | `SurroundingRectangle(point)` | `pass mobjects` | Pass mobjects to SurroundingRectangle, wrapping a bare point in a Dot first. |
| 24 | `requires-python\|Requires-Python\|python_requires` | `an interpreter outside 3.11 or 3.12` | `uv venv --python 3.12` | Recreate the venv with uv venv --python 3.12; preflight.py is the detector for an interpreter outside 3.11 or 3.12, so rerun it before rendering. |

## Silent scenes and the render cache

- Scenes render silent. `narrate.py` synthesizes each beat's narration and `assemble.py`
  joins it to the picture, so a scene never calls `add_sound`, and ManimCE's cache holds
  only pictures: a re-render reuses every play whose objects, arguments and run time are
  unchanged.
- `render.py` renders each scene in its own process with the cache on, and retries a hung
  render once with `--disable_caching`.
- One measured exception: a warm re-render of a 3D scene with an ambient camera rotation,
  which is what `orbit_with_hud` runs, rendered the segment after the rotation again, most
  likely because the cached wait skipped the rotation's updater and left the camera where
  the rotation began. Such a re-render can show a camera jump after the orbit that the code
  does not contain, so judge an orbiting scene from a cold render before changing its code.
