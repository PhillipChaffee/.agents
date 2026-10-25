# ManimGL to ManimCE translation map

This map translates the Manim idioms used in the 3Blue1Brown neural-network and
transformer series (written for Grant Sanderson's fork, ManimGL) into Manim
Community Edition (ManimCE) idioms, and records the ManimCE features, gotchas
and idioms an agent needs to write ManimCE scenes programmatically. Every claim
is grounded in a source path with line numbers or marked unverified.

## Scope, versions and evidence

Path prefixes used in citations:

- `CE` is `/home/user/ManimCommunity/manim/` (ManimCE, shallow clone of
  [ManimCommunity/manim](https://github.com/ManimCommunity/manim), commit
  `bb380986`, dated 2026-10-24).
- `GL` is `/home/user/3b1b/manim/` (ManimGL, shallow clone of
  [3b1b/manim](https://github.com/3b1b/manim), commit `fafa083a`, dated
  2026-09-09).
- `V` is `/home/user/3b1b/videos/` (the read-only series source,
  [3b1b/videos](https://github.com/3b1b/videos)).

Versions:

| Package | Version in clone | Evidence | PyPI release |
| --- | --- | --- | --- |
| ManimCE (`manim`) | 0.22.0 | `CE pyproject.toml:3`; Python `>=3.11` at `CE pyproject.toml:23` | 0.22.0, uploaded 2026-10-08 ([PyPI page](https://pypi.org/project/manim/)) |
| ManimGL (`manimgl`) | 1.7.2 | `GL setup.cfg:2-3` | 1.7.2, uploaded 2024-12-13 ([PyPI page](https://pypi.org/project/manimgl/)); the clone is ~21 months of commits ahead of that release under the same version string |
| `manim-voiceover` | not cloned | PyPI metadata only | 0.4.0, uploaded 2026-06-14, requires Python `>=3.11` ([PyPI page](https://pypi.org/project/manim-voiceover/)) |

The ManimCE documentation site is blocked in this container, so every
documentation claim below cites the docs source under `CE docs/source/`
instead. The series code imports everything through `from manimlib import *`
plus 3b1b's own `custom/` package (`V manim_imports_ext.py:1-14`), and renders
with 3b1b's `V custom_config.yml` (4K at 30 fps, black background, CMU Serif
font; lines 20-22, 27).

### How the series uses Manim (frequency evidence)

Counts come from a tokenizer pass over the 29 Python files in `V _2017/nn`,
`V _2024/transformers` and `V custom` (script output saved at
`/tmp/claude-0/-home-user--agents/b713d8f3-7c52-540b-8252-65c41f426313/scratchpad/freq_out.txt`).
Only names defined in `GL manimlib/` were counted as Manim names.

Most-used classes (occurrences):

| Rank | ManimGL class | Count | Rank | ManimGL class | Count |
| --- | --- | --- | --- | --- | --- |
| 1 | `VGroup` | 1339 | 21 | `Transform` | 99 |
| 2 | `FadeIn` | 614 | 22 | `FadeTransform` | 89 |
| 3 | `FadeOut` | 482 | 23 | `Brace` | 74 |
| 4 | `Text` | 351 | 24 | `Vector` | 73 |
| 5 | `LaggedStartMap` | 333 | 25 | `GrowFromCenter` | 71 |
| 6 | `Write` | 310 | 26 | `Scene` | 55 |
| 7 | `ShowCreation` | 270 | 27 | `DecimalNumber` | 47 |
| 8 | `SurroundingRectangle` | 220 | 28 | `ImageMobject` | 47 |
| 9 | `LaggedStart` | 203 | 29 | `Restore` | 44 |
| 10 | `OldTexText` | 199 | 30 | `TexText` | 43 |
| 11 | `Tex` | 186 | 31 | `ApplyMethod` | 40 |
| 12 | `MoveToTarget` | 184 | 32 | `Dot` | 34 |
| 13 | `OldTex` | 157 | 33 | `SVGMobject` | 34 |
| 14 | `ReplacementTransform` | 154 | 34 | `Integer` | 32 |
| 15 | `TransformFromCopy` | 149 | 35 | `Rectangle` | 31 |
| 16 | `Arrow` | 145 | 36 | `FadeInFromPoint` | 26 |
| 17 | `InteractiveScene` | 127 | 37 | `ChangingDecimal` | 23 |
| 18 | `Line` | 123 | 38 | `DrawBorderThenFill` | 22 |
| 19 | `GrowArrow` | 111 | 39 | `ScreenRectangle` | 22 |
| 20 | `Group` | 104 | 40 | `Indicate` | 21 |

Also used 8-21 times: `AnimationGroup`, `SpeechBubble`, `FlashAround`,
`FullScreenRectangle`, `ShowCreationThenDestruction`, `UpdateFromFunc`,
`NumberPlane`, `VShowPassingFlash`, `Square`, `Underline`,
`BackgroundRectangle`, `CountInFrom`, `GrowFromPoint`, `NumberLine`, `Rotate`,
`ThreeDAxes`, `ThoughtBubble`, `ShowIncreasingSubsets`, `UpdateFromAlphaFunc`,
`MaintainPositionRelativeTo`, `TransformMatchingStrings`, `ApplyFunction`,
`FadeTransformPieces`, `DashedLine`, `Cross`, `Union`, `Succession`, `VFadeIn`,
`VFadeInThenOut`, `Axes`, `FullScreenFadeRectangle`.

Most-used methods and attributes: `play` 1913, `wait` 1143, `next_to` 960,
`add` 783, `.target` 591, `.animate` 501, `copy` 483, `set_color` 447,
`set_stroke` 418, `move_to` 385, `scale` 344, `set_fill` 336, `shift` 275,
`set_height` 270, `to_edge` 238, `arrange` 221, `set_opacity` 201,
`generate_target` 165, `rotate` 149, `get_center` 147, `reorient` 138,
`self.frame` 113, `save_state` 107, `set_width` 105, `set_backstroke` 41,
`insert_n_curves` 37, `replicate` 34, `become` 30, `add_updater` 28,
`get_grid` 25, `set_max_width` 23, `c2p` 22.

Most-used keyword arguments: `buff` 709, `run_time` 672, `lag_ratio` 565,
`font_size` 252, `color` 204, `opacity` 201, `aligned_edge` 106,
`rate_func` 103, `shift` 101, `time_span` 88, `stroke_width` 87,
`path_arc` 85, `about_edge` 81, `about_point` 41, `remover` 37.

Most-used constants: `UP` 834, `RIGHT` 806, `DOWN` 781, `LEFT` 659,
`SMALL_BUFF` 301, `YELLOW` 251, `WHITE` 219, `BLUE` 172, `DEGREES` 142,
`RED` 141, `BLACK` 114, `MED_LARGE_BUFF` 91, `MED_SMALL_BUFF` 89,
`ORIGIN` 84, `LARGE_BUFF` 76, `PI` 70, `TEAL` 67, `GREEN` 66, `GREY_B` 58,
`FRAME_WIDTH` 55, `OUT` 49, `UL` 48, `FRAME_HEIGHT` 39.

Most-used functions: `there_and_back` 45, `interpolate` 33, `cross` 29,
`wiggle` 27, `normalize` 27, `linear` 21, `sigmoid` 17,
`random_bright_color` 14, `smooth` 13, `squish_rate_func` 10, `get_norm` 10,
`interpolate_color` 9, `midpoint` 8, `turn_animation_into_updater` 6,
`index_labels` 6, `always_redraw` 5.

## Translation table

Each row gives the ManimGL name, the ManimCE equivalent or idiom, gotchas, and
evidence. "Same" means the name and the core signature match closely enough
that code ports without edits beyond the import line.

### Scenes and camera

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `from manimlib import *` | `from manim import *` | CE also installs a `manimce` executable; if both packages are installed the `manim` command may be ManimGL's and reports "no scenes inside that module". Use `manimce` or `python -m manim`. | `CE pyproject.toml:55-57`; `CE docs/source/faq/general.md` (first entry) |
| `InteractiveScene` (127 uses) | `Scene` | CE has no selection, mouse grab or `checkpoint_paste`; `Scene.interactive_embed` exists but needs the OpenGL renderer and is flaky with recent IPython. Delete all `self.embed()` calls. | `GL manimlib/scene/interactive_scene.py:60`; `GL manimlib/scene/scene_embed.py:194`; `CE manim/scene/scene.py:1439`; `CE docs/source/faq/opengl.md` |
| `CONFIG = {...}` class dicts (2017 code) | Class attributes or `__init__` keyword arguments | CE dropped `CONFIG` in v0.2.0. | `CE docs/source/faq/general.md` ("what do I do with CONFIG dictionaries") |
| `self.frame` (113 uses), `self.frame.set_height(h)`, `.move_to(p)`, `.animate.reorient(...)` for 2D pans and zooms | `MovingCameraScene`; `self.camera.frame.animate.set(width=w).move_to(p)`, `.scale(k)`, `self.camera.frame.save_state()` then `Restore(self.camera.frame)`; `self.camera.auto_zoom(mobjects, margin, animate=True)` | A plain `Scene` camera has no `frame`; you must subclass `MovingCameraScene`. GL `set_height` becomes `.set(height=...)` or `.scale`. | `GL manimlib/scene/scene.py:114`; `GL manimlib/camera/camera_frame.py:25,178-196`; `CE manim/scene/moving_camera_scene.py:17-64,104-121`; `CE manim/camera/moving_camera.py:62-117,170-189` |
| `self.frame.reorient(theta_deg, phi_deg, gamma_deg, center, height)` (138 uses) for 3D views | `ThreeDScene.set_camera_orientation(phi, theta, gamma, zoom, focal_distance, frame_center)` (instant) and `move_camera(..., added_anims=[...])` (animated); `begin_ambient_camera_rotation(rate)` | GL takes degrees; CE takes radians (multiply by `DEGREES`). GL `height` maps to `zoom` (inverse relation) and `center` to `frame_center`. Whether GL theta/phi conventions match CE one-to-one is unverified (both call theta the azimuth and phi the polar angle). | `GL manimlib/camera/camera_frame.py:178-196`; `CE manim/scene/three_d_scene.py:31,55-100,102,211-240` |
| `mob.fix_in_frame()` (HUD elements in 3D) | `ThreeDScene.add_fixed_in_frame_mobjects(*mobs)`; `add_fixed_orientation_mobjects` | CE method lives on the scene, not the mobject, and only takes effect with the Cairo renderer path shown. | `GL manimlib/mobject/mobject.py:1894`; `CE manim/scene/three_d_scene.py:330,357-380` |
| GL `ThreeDScene` (only enables depth test) | CE `ThreeDScene` (camera orientation, ambient rotation, fixed-in-frame) | Different purposes; GL does 3D in any `Scene` via `self.frame`. | `GL manimlib/scene/scene.py:929-934`; `CE manim/scene/three_d_scene.py:31` |
| `self.play(*anims, run_time=, rate_func=, lag_ratio=)` | Same; extra `subcaption`, `subcaption_duration`, `subcaption_offset` | `run_time <= 0` raises `ValueError`; sub-frame run times are clamped with a warning. | `CE manim/scene/scene.py:1188-1241,1141-1168` |
| `self.wait(t)` | `self.wait(duration, stop_condition, frozen_frame)`; `self.pause(t)`; `self.wait_until(cond, max_time)` | `frozen_frame=True` skips updaters for a still frame. | `CE manim/scene/scene.py:1242-1311` |
| `self.add`, `self.remove`, `self.clear`, `bring_to_front`, `bring_to_back` | Same; plus `add_foreground_mobjects` | `Scene.add` order defines draw order unless `z_index` is set. | `GL manimlib/scene/scene.py:315-385`; `CE manim/scene/scene.py:517-611,799-909` |
| `self.add_sound(file, time_offset, gain)` | Same signature | Path resolves relative to `assets_dir`. | `GL manimlib/scene/scene.py:643`; `CE manim/scene/scene.py:1768-1810` |
| Scene-level `save_state`/`restore_state` | None (per-mobject `save_state` + `Restore` only) | | `GL manimlib/scene/scene.py:661-664`; `CE manim/mobject/mobject.py:2281-2293` |
| `set_floor_plane` | None | 3b1b-specific axis convention helper. | `GL manimlib/scene/scene.py:725` |
| (none) | `self.next_section(name, section_type, skip_animations)` | Enables per-section output videos; see the features section. | `CE manim/scene/scene.py:378-388` |

### Text and formulas

The single most error-prone swap: GL `Tex` is math mode and GL `TexText` is
text mode; CE `MathTex` is math mode and CE `Tex` is text mode.

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `Tex(r"...")` (186 uses; `tex_environment = "align*"`) | `MathTex(r"...")` (`tex_environment="align*"`) | Name swap. Both require a LaTeX toolchain. | `GL manimlib/mobject/svg/tex_mobject.py:35-36`; `CE manim/mobject/text/tex_mobject.py:227,278-284` |
| `TexText(r"...")` (43 uses; `tex_environment = ""`) | `Tex(r"...")` (`tex_environment="center"`) | Name swap. Inline math needs `$...$` in CE `Tex`. | `GL manimlib/mobject/svg/tex_mobject.py:276-277`; `CE manim/mobject/text/tex_mobject.py:614,631-635` |
| `OldTex("a", "+", "b")` (157 uses) | `MathTex("a", "+", "b", arg_separator=" ")` | One submobject per string argument in both. | `GL manimlib/mobject/svg/old_tex_mobject.py:181`; `CE manim/mobject/text/tex_mobject.py:278-284` |
| `OldTexText("word", "word")` (199 uses) | `Tex("word", "word", arg_separator="")` | GL `OldTexText(math_mode=False)`; CE `Tex` is text mode already. | `GL manimlib/mobject/svg/old_tex_mobject.py:317-330`; `CE manim/mobject/text/tex_mobject.py:631-635` |
| `Tex(..., isolate=["x", "y"], t2c={...})` | `MathTex(..., substrings_to_isolate=["x", "y"], tex_to_color_map={...})` or `{{ x }}` double-brace groups inside one string | CE `{{` must start the string or follow whitespace, so `\frac{{{n}}}{k}` is not split. | `GL manimlib/mobject/svg/tex_mobject.py:38-48`; `CE manim/mobject/text/tex_mobject.py:239-258,282-283` |
| `tex["x"]`, `tex.select_part("x")`, `select_parts` | `tex.get_part_by_tex("x")`, `set_color_by_tex`, `set_opacity_by_tex`, `set_color_by_tex_to_color_map`, `index_of_part` | CE lookup works only on substrings that were isolated (separate args, `substrings_to_isolate`, or `{{ }}`). | `GL manimlib/mobject/svg/string_mobject.py:546-561`; `CE manim/mobject/text/tex_mobject.py:543-602` |
| `tex.make_number_changeable("3")` | None; place a `DecimalNumber` with `move_to(part)` and keep it with an updater | | `GL manimlib/mobject/svg/tex_mobject.py:234-240` |
| `Text("...", font=, font_size=, t2c=, t2s=, t2w=, slant=, weight=, lsh=, isolate=)` (351 uses) | `Text("...", font=, font_size=, t2c=, t2f=, t2g=, t2s=, t2w=, slant=, weight=, line_spacing=, disable_ligatures=)` | GL default `disable_ligatures=True`; CE default `False`, so set it when you index characters. GL `lsh` is CE `line_spacing`. GL `isolate` has no CE analogue; CE `Text` is indexable per glyph and sliceable. GL default font is Consolas (3b1b uses CMU Serif); CE default is Pango `sans`. | `GL manimlib/mobject/svg/text_mobject.py:136-165,400-407`; `GL manimlib/default_config.yml:102`; `V custom_config.yml:27`; `CE manim/mobject/text/text_mobject.py:448-472,480-490`; `CE docs/source/guides/using_text.rst` |
| `MarkupText` | `MarkupText` (Pango markup) | Same idea; CE recommends it when `t2c` hits ligature problems. | `CE manim/mobject/text/text_mobject.py:877,1181-1199` |
| (none) | `Paragraph` | Multi-line text as a `VGroup` of lines. | `CE manim/mobject/text/text_mobject.py:114` |
| `Code(..., language=, code_style=, font=, font_size=)` | `Code(code_file=None, code_string=None, language=, formatter_style="vim", tab_width, add_line_numbers, background="rectangle" or "window", background_config, paragraph_config)` | CE uses Pygments styles; GL `code_style` is CE `formatter_style`; font goes in `paragraph_config={"font": ...}`. | `GL manimlib/mobject/svg/text_mobject.py:438-449`; `CE manim/mobject/text/code_mobject.py:30-60,172-183` |
| `BulletedList`, `Title` | Same names, `Tex`-based | LaTeX required. | `GL manimlib/mobject/svg/special_tex.py:18,61`; `CE manim/mobject/text/tex_mobject.py:646,722` |
| (none) | `Typst`, `MathTypst` | Formula rendering without a TeX distribution (optional extra `manim[typst]`). | `CE manim/mobject/text/typst_mobject.py:1-13,274,763`; `CE pyproject.toml:77-79` |
| `Text.set_default` pattern | `Text.set_default(font="CMU Serif")`, `MathTex.set_default(...)` (any `Mobject` subclass) | Class-wide default override; call with no kwargs to reset. | `CE manim/mobject/mobject.py:262-312` |

### Animations: creation, fading, transforms

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `ShowCreation(m)` (270 uses) | `Create(m, lag_ratio=1.0)` | Name change only. | `GL manimlib/animation/creation.py:48`; `CE manim/animation/creation.py:140,167-173` |
| `Uncreate`, `DrawBorderThenFill`, `Write`, `ShowIncreasingSubsets`, `ShowSubmobjectsOneByOne`, `AddTextWordByWord` | Same names; CE adds `Unwrite`, `AddTextLetterByLetter`, `RemoveTextLetterByLetter`, `TypeWithCursor`, `SpiralIn` | CE `Write` auto run time: 1 s if fewer than 15 family members with points, else 2 s; `lag_ratio = min(4/len, 0.2)`. | `CE manim/animation/creation.py:180,213,291,344-354,492,544,633,654` |
| `FadeIn(m, shift=UP, scale=0.8)` (614 uses), `FadeOut(m, shift=DOWN)` (482 uses) | Same (`shift`, `target_position`, `scale`) | CE `FadeIn/FadeOut` accept several mobjects. | `GL manimlib/animation/fading.py:35,47`; `CE manim/animation/fading.py:34-57,98,136,146,184` |
| `FadeInFromPoint(m, point)`, `FadeOutToPoint(m, point)` | `FadeIn(m, target_position=point, scale=0.1)`, `FadeOut(m, target_position=point, scale=0.1)` | Approximation; visual equivalence unverified. | `GL manimlib/animation/fading.py:71-90`; `CE manim/animation/fading.py:52-57` |
| `VFadeIn`, `VFadeOut` (stroke and fill opacity only) | `FadeIn`, `FadeOut` | CE fades by transforming to a faded copy; close enough for teaching videos. | `GL manimlib/animation/fading.py:157,182`; `CE manim/animation/fading.py:34-57` |
| `VFadeInThenOut(m)` | `Succession(FadeIn(m), FadeOut(m))` or `FadeIn(m, rate_func=there_and_back, remover=True)` | | `GL manimlib/animation/fading.py:206`; `CE manim/animation/composition.py:198`; `CE manim/animation/animation.py:99-112` |
| `FadeTransform(a, b)` (89 uses), `FadeTransformPieces` | Same; CE adds `stretch=True`, `dim_to_match=1` | | `GL manimlib/animation/fading.py:91,147`; `CE manim/animation/transform.py:812-860,919` |
| `Transform`, `ReplacementTransform`, `TransformFromCopy`, `MoveToTarget`, `ApplyMethod`, `ApplyFunction`, `ApplyMatrix`, `Restore`, `CyclicReplace`, `Swap`, `ScaleInPlace`, `ShrinkToCenter`, `FadeToColor` | Same names | `MoveToTarget` raises `ValueError` without `generate_target()`; `Restore` raises without `save_state()`. `Transform(path_arc=...)` works in both. | `GL manimlib/animation/transform.py:24-324`; `CE manim/animation/transform.py:58-83,253,307,406-440,454,544,562,580,598,624,638,704,753` |
| `self.play(mob.shift, UP)` (2017-era method passing) | `self.play(mob.animate.shift(UP))` or `ApplyMethod(mob.shift, UP)` | CE raises `TypeError: Passing Mobject methods to Scene.play is no longer supported. Use Mobject.animate instead.` | `CE manim/scene/scene.py:1020-1031` |
| `mob.animate.shift(UP).set_color(RED)`; `mob.animate(run_time=2).shift(UP)` (501 uses) | Same, including the call form `mob.animate(run_time=2, rate_func=linear).shift(UP)` | Call form must come before method access and only once. Chaining is unsupported for methods decorated with `override_animate`. `.animate` interpolates start to end, so rotations via `.animate.rotate` take straight-line paths; use `Rotate`. | `GL manimlib/mobject/mobject.py:176,2158`; `CE manim/mobject/mobject.py:313,3560-3590` |
| `TransformMatchingStrings(a, b)`, `TransformMatchingTex` | `TransformMatchingTex(a, b, transform_mismatches=False, fade_transform_mismatches=False, key_map=None)`; `TransformMatchingShapes` for non-text | CE matches on `tex_string` of isolated parts; isolate shared parts with `{{ }}` or `substrings_to_isolate`. | `GL manimlib/animation/transform_matching_parts.py:118-189`; `CE manim/animation/transform_matching_parts.py:175,237-276` |
| `GrowArrow`, `GrowFromCenter`, `GrowFromPoint`, `GrowFromEdge` | Same; CE adds `SpinInFromNothing` | | `GL manimlib/animation/growing.py:15-51`; `CE manim/animation/growing.py:49,102,136,176,214` |
| `Rotate(m, angle, axis, about_point)`, `Rotating` | Same names | CE `Rotating` defaults: `angle=TAU`, `run_time=5`, `rate_func=linear`. | `GL manimlib/animation/rotation.py:17,58`; `CE manim/animation/rotation.py:21,88-98,115,155-163` |
| `Broadcast`, `Homotopy`, `ComplexHomotopy`, `PhaseFlow`, `MoveAlongPath`, `ApplyWave` | Same names | | `GL manimlib/animation/specialized.py:16`; `GL manimlib/animation/movement.py:17-105`; `CE manim/animation/specialized.py:15`; `CE manim/animation/movement.py:31-173`; `CE manim/animation/indication.py:358` |

### Animations: composition, timing, indication

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `LaggedStart(*anims, lag_ratio=)` (203 uses) | Same | Default `lag_ratio` is `DEFAULT_LAGGED_START_LAG_RATIO` in both (0.05 in GL). | `GL manimlib/animation/composition.py:24,157`; `CE manim/animation/composition.py:297-342` |
| `LaggedStartMap(FadeIn, group, lag_ratio=, run_time=2, shift=UP)` (333 uses) | `LaggedStartMap(FadeIn, group, arg_creator=None, run_time=2, lag_ratio=, shift=UP)` | In both, extra kwargs go to each per-submobject animation. GL `anim_func` may be any callable; CE expects an `Animation` class (a lambda returning an animation also works since it is only called). | `GL manimlib/animation/composition.py:167-187`; `CE manim/animation/composition.py:351-420` |
| `AnimationGroup(*anims, lag_ratio=, group=)`, `Succession` | Same | CE `AnimationGroup` default `rate_func=linear`. | `GL manimlib/animation/composition.py:27,123`; `CE manim/animation/composition.py:30-61,198` |
| `Animation(..., time_span=(a, b))` (88 uses) | None. Emulate with `Succession(Wait(a), anim)` inside an `AnimationGroup`, or `rate_func=squish_rate_func(smooth, a/T, b/T)` with `run_time=T` | With `squish_rate_func` the mobject is already at its alpha-0 state during the delay (fine for transforms, visible for introducers). | `GL manimlib/animation/animation.py:24-69,176-219`; `CE manim/utils/rate_functions.py:274`; `CE manim/animation/animation.py:584` |
| `Animation(remover=True)` | Same; CE adds `introducer`, `reverse_rate_function`, `suspend_mobject_updating=True` | GL defaults `suspend_mobject_updating=False`; CE defaults `True`, so updaters pause while a mobject is animated unless you pass `False`. | `GL manimlib/animation/animation.py:37-43`; `CE manim/animation/animation.py:99-112` |
| `Indicate(m, scale_factor=1.2, color=YELLOW)` | `Indicate(m, scale_factor=1.2, color=PURE_YELLOW, rate_func=there_and_back)` | Same hex `#FFFF00` (see colors). | `GL manimlib/animation/indication.py:73`; `CE manim/animation/indication.py:125,152-158` |
| `FocusOn(point)`, `Flash(point)` | Same | CE `Flash(point, line_length=0.2, num_lines=12, flash_radius=0.1, color=PURE_YELLOW, time_width=1)`. | `CE manim/animation/indication.py:72,98-105,171,222-233` |
| `FlashAround(m)`, `FlashUnder`, `ShowPassingFlashAround`, `CircleIndicate`, `ShowCreationThenDestructionAround` | `Circumscribe(m, shape=Rectangle or Circle, fade_in=False, fade_out=False, time_width=0.3, buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1, stroke_width=4)` | Closest built-in; GL `FlashAround` draws a passing flash on a surrounding rectangle, which is what `Circumscribe` does. | `GL manimlib/animation/indication.py:142,255-328`; `CE manim/animation/indication.py:571,613-625` |
| `VShowPassingFlash(m, time_width=)`, `ShowPassingFlash` | `ShowPassingFlash(vmobject, time_width=0.1)` | Apply to a copy with heavier stroke for the 3b1b "light sweep". | `GL manimlib/animation/indication.py:165,194`; `CE manim/animation/indication.py:274,308-310` |
| `ShowCreationThenDestruction(m)` | `ShowPassingFlash(m, time_width=1.0)` | Approximation. | `GL manimlib/animation/indication.py:284`; `CE manim/animation/indication.py:274` |
| `ShowCreationThenFadeOut(m)` | `Succession(Create(m), FadeOut(m))` | | `GL manimlib/animation/indication.py:289`; `CE manim/animation/composition.py:198` |
| `WiggleOutThenIn(m)` | `Wiggle(m, scale_value=1.1, rotation_angle=0.01*TAU, n_wiggles=6)` | | `GL manimlib/animation/indication.py:355`; `CE manim/animation/indication.py:488,521-531` |
| `TurnInsideOut`, `FlashyFadeIn` | None | Rare in the corpus. | `GL manimlib/animation/indication.py:397,405` |
| `UpdateFromFunc`, `UpdateFromAlphaFunc`, `MaintainPositionRelativeTo` | Same | CE ones default `suspend_mobject_updating=False`. | `GL manimlib/animation/update.py:13-53`; `CE manim/animation/updaters/update.py:18-62` |
| `ChangingDecimal(num, func)`, `ChangeDecimalToValue(num, target)` | Same | | `GL manimlib/animation/numbers.py:14,37`; `CE manim/animation/numbers.py:17,74` |
| `CountInFrom(num, source)` | `num.set_value(source)` then `ChangeDecimalToValue(num, target)` | | `GL manimlib/animation/numbers.py:52` |
| `always_redraw(func, *args)` | `always_redraw(func)` (no args; wrap in a lambda) | Rebuilds the mobject every frame; prefer mutating updaters for heavy mobjects. | `GL manimlib/mobject/mobject_update_utils.py:55-58`; `CE manim/animation/updaters/mobject_update_utils.py:67-111` |
| `always(mob.method, *args)`, `f_always(mob.method, *generators)` | Same functions, exported | | `GL manimlib/mobject/mobject_update_utils.py:26-52`; `CE manim/animation/updaters/mobject_update_utils.py:5-14,41,49` |
| `mob.always.method(*args)` builder; `mob.f_always.method(lambda: ...)` | `mob.always.method(*args)` exists (0.20.0); no `f_always` builder, use the `f_always` function | | `GL manimlib/mobject/mobject.py:187,196`; `CE manim/mobject/mobject.py:423-456,3622-3636`; `CE docs/source/changelog/0.20.0-changelog.md:25-26` |
| `turn_animation_into_updater(anim, cycle=)`, `cycle_animation`, `always_shift`, `always_rotate` | Same; CE adds `delay=` | | `GL manimlib/mobject/mobject_update_utils.py:61-131`; `CE manim/animation/updaters/mobject_update_utils.py:112,151,184,247` |
| `mob.add_updater(func)` (28 uses) | `mob.add_updater(func, index=None, call_updater=False)` | Updaters run only for mobjects added to the scene (`Scene.update_mobjects` iterates `self.mobjects`), and are suspended during animations by default. `dt` is passed only if the function declares a `dt` parameter. | `GL manimlib/mobject/mobject.py:823`; `CE manim/mobject/mobject.py:1148-1231`; `CE manim/scene/scene.py:409-420` |

### Mobject methods, groups, layering

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `VGroup(*vmobs)` (1339 uses), `Group(*mobs)` | Same | `VGroup` raises `TypeError` for non-`VMobject` members (for example `ImageMobject`); use `Group`. | `GL manimlib/mobject/types/vectorized_mobject.py:1393`; `CE manim/mobject/types/vectorized_mobject.py:2179,2253-2362`; `CE manim/mobject/mobject.py:3545` |
| `set_height(h, stretch=False)` (270 uses), `set_width(w)` | `scale_to_fit_height(h)`, `stretch_to_fit_height(h)`, or `mob.height = h`; `scale_to_fit_width`, `stretch_to_fit_width`, `mob.width = w` | CE synthesizes `set_*`/`get_*` names through `__getattr__` with a `DeprecationWarning`; do not rely on them. | `GL manimlib/mobject/mobject.py:1162-1165`; `CE manim/mobject/mobject.py:876-904,907-995,1898-1998` |
| `get_width()`, `get_height()` | `mob.width`, `mob.height`, `mob.depth` properties | | `CE manim/mobject/mobject.py:907,943,979` |
| `set_max_width(w)`, `set_max_height`, `set_min_width` | None; write `if mob.width > w: mob.scale_to_fit_width(w)` | | `GL manimlib/mobject/mobject.py:1171-1186` |
| `replicate(n)` (34 uses) | `VGroup(*(mob.copy() for _ in range(n)))` | | `GL manimlib/mobject/mobject.py:755` |
| `get_grid(n_rows, n_cols, buff=)` (25 uses) | `.arrange_in_grid(rows, cols, buff, cell_alignment, row_alignments, col_alignments, flow_order="rd")` on the replicated group | Raises `ValueError` when rows times cols is too small. | `GL manimlib/mobject/mobject.py:759`; `CE manim/mobject/mobject.py:2767-2777,2901` |
| `arrange(direction, buff, aligned_edge)`, `arrange_in_grid`, `arrange_to_fit_width` | `arrange`, `arrange_in_grid`; no `arrange_to_fit_width` | | `GL manimlib/mobject/mobject.py:507-580`; `CE manim/mobject/mobject.py:2737-2777` |
| `next_to(target, direction, buff, aligned_edge, submobject_to_align, index_of_submobject_to_align)` (960 uses) | Same (plus `coor_mask`) | | `GL manimlib/mobject/mobject.py:1083`; `CE manim/mobject/mobject.py:1808-1817` |
| `to_edge`, `to_corner`, `align_to`, `match_x`, `match_y`, `match_width`, `match_height`, `match_color`, `set_x`, `set_y`, `move_to`, `shift`, `scale(about_point=, about_edge=)`, `rotate`, `flip`, `stretch`, `center`, `surround`, `get_center`, `get_top`, `get_bottom`, `get_left`, `get_right`, `get_corner`, `copy`, `become`, `generate_target`, `save_state`, `restore`, `fade`, `set_color`, `set_color_by_gradient`, `set_submobject_colors_by_gradient`, `set_opacity`, `sort`, `shuffle` | Same | GL `recurse=` keyword is `family=` in CE. | `CE manim/mobject/mobject.py:1391-1808,2033-2077,2165-2290,2432-2605,3022-3036,3321` |
| `set_stroke(color, width, opacity, background=)` (418 uses), `set_fill(color, opacity)` (336 uses) | `set_stroke(color, width, opacity, background=False, family=True)`, `set_fill(color, opacity, family=True)` | Positional order matches. | `GL manimlib/mobject/types/vectorized_mobject.py:266,326`; `CE manim/mobject/types/vectorized_mobject.py:282,332-345` |
| `set_backstroke(color=BLACK, width=)` (41 uses) | `set_stroke(BLACK, width, background=True)`, `set_background_stroke(color=, width=)`, or constructor kwargs `background_stroke_color`, `background_stroke_width` | CE default background stroke width is 0. | `GL manimlib/mobject/types/vectorized_mobject.py:356`; `CE manim/mobject/types/vectorized_mobject.py:109-130,391-395` |
| `set_shading`, `set_flat_stroke`, `set_anti_alias_width`, `apply_depth_test`, `deactivate_depth_test`, `set_clip_plane`, `set_joint_type` | None (GPU-only features); CE has `set_sheen`, `set_shade_in_3d`, `joint_type`, `cap_style` kwargs | Delete these calls when porting. | `GL manimlib/mobject/mobject.py:1445,1905-1915`; `GL manimlib/mobject/types/vectorized_mobject.py:494,570,599`; `CE manim/mobject/types/vectorized_mobject.py:120,130,363,717,787` |
| `insert_n_curves(n)` (37 uses), `pointwise_become_partial`, `get_subcurve`, `point_from_proportion`, `set_points_as_corners`, `set_points_smoothly`, `make_smooth`, `start_new_path`, `add_line_to`, `get_arc_length` | Same | | `CE manim/mobject/types/vectorized_mobject.py:883,987,1113,1160,1199,1623,1797,1895,1990,2088` |
| `set_z_index(z, recurse=True)` | `set_z_index(z, family=True)` | CE camera sorts by `z_index` then insertion order (`use_z_index=True` default). | `GL manimlib/mobject/mobject.py:1232`; `CE manim/mobject/mobject.py:3489-3530`; `CE manim/camera/camera.py:91,108` |
| `add_background_rectangle()` | Same; `BackgroundRectangle(m, color=None, fill_opacity=0.75, buff=0)` | | `CE manim/mobject/mobject.py:2108`; `CE manim/mobject/geometry/shape_matchers.py:83,108-115` |
| `index_labels(m)` (debug) | Same | | `GL manimlib/utils/debug.py:21`; `CE manim/utils/debug.py:25` |
| (none) | `Mobject.set(**kwargs)`, `Mobject.set_default(**kwargs)` | `set_default` changes a class's constructor defaults globally. | `CE manim/mobject/mobject.py:262-312,803` |

### Geometry and shape matchers

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `Line(start, end, buff=, path_arc=)` (123 uses), `DashedLine` | Same | | `GL manimlib/mobject/geometry.py:655,808`; `CE manim/mobject/geometry/line.py:65,95,282` |
| `Arrow(start, end, buff=MED_SMALL_BUFF, thickness=3, tip_width_ratio=5, tip_angle=PI/3, max_tip_length_to_length_ratio=0.5, max_width_to_length_ratio=)` (145 uses) | `Arrow(start, end, buff=MED_SMALL_BUFF, stroke_width=6, max_tip_length_to_length_ratio=0.25, max_stroke_width_to_length_ratio=5, tip_shape=ArrowTriangleFilledTip)` | GL arrows are filled polygons parameterized by `thickness`; CE arrows are strokes plus a tip. Map `thickness` to `stroke_width` by eye. CE `Arrow.scale` keeps tip size unless `scale_tips=True`. | `GL manimlib/mobject/geometry.py:1032-1060`; `CE manim/mobject/geometry/line.py:503,591-612`; `CE manim/mobject/geometry/tips.py:31-336` |
| `Vector(direction)` (73 uses), `DoubleArrow` | Same | | `CE manim/mobject/geometry/line.py:714,819` |
| `Dot(point, radius=0.08)`, `Circle`, `Ellipse`, `Arc`, `AnnularSector`, `Sector`, `Annulus`, `CubicBezier` | Same (radius default 0.08 in both) | | `GL manimlib/mobject/geometry.py:38,423`; `CE manim/constants.py:163`; `CE manim/mobject/geometry/arc.py:305,634,789,917,948,1038,1059,1115` |
| `Rectangle(width, height)`, `Square(side_length)`, `RoundedRectangle`, `Polygon`, `RegularPolygon`, `Triangle`, `Elbow` | Same | | `CE manim/mobject/geometry/polygram.py:311,436,570,595,690,725`; `CE manim/mobject/geometry/line.py:465` |
| `SurroundingRectangle(m, buff=SMALL_BUFF, color=YELLOW)` (220 uses) | `SurroundingRectangle(*mobs, color=PURE_YELLOW, buff=SMALL_BUFF, corner_radius=0.0)` | GL `YELLOW` and CE `PURE_YELLOW` are both `#FFFF00`; CE `YELLOW` is `#F7D96F`, so a naive `color=YELLOW` port changes the look. | `GL manimlib/mobject/shape_matchers.py:22-30`; `CE manim/mobject/geometry/shape_matchers.py:26,50-55` |
| `Underline(m)`, `Cross(m)` | `Underline(m)`, `Cross(m, stroke_color=RED, stroke_width=6, scale_factor=1)` | | `CE manim/mobject/geometry/shape_matchers.py:153,178-183,195` |
| `Brace(m, direction)` (74 uses), `brace.get_text`, `brace.get_tex` | Same; CE `get_text` returns `Tex`, `get_tex` returns `MathTex`; also `BraceLabel`, `BraceText`, `BraceBetweenPoints`, `ArcBrace` | Both `get_text` and `get_tex` require LaTeX in CE; the brace itself is an SVG path and does not. | `GL manimlib/mobject/svg/brace.py:32`; `CE manim/mobject/svg/brace.py:33,68-78,157,176,205,285,340,385` |
| `ScreenRectangle`, `FullScreenRectangle` | Same (`ScreenRectangle(aspect_ratio=16/9, height=4)`; `FullScreenRectangle` sets `height = config.frame_height`) | | `GL manimlib/mobject/frame.py:12,26`; `CE manim/mobject/frame.py:18-41` |
| `FullScreenFadeRectangle` | `FullScreenRectangle(fill_color=BLACK, fill_opacity=0.7, stroke_width=0)` | | `GL manimlib/mobject/frame.py:44` |
| `Union`, `Difference` | `Union`, `Difference`, `Intersection`, `Exclusion` | | `GL manimlib/mobject/boolean_ops.py:52,66`; `CE manim/mobject/geometry/boolean_ops.py:150,193,231,286` |
| `VectorizedPoint`, `Point` | Same | | `CE manim/mobject/types/vectorized_mobject.py:2746`; `CE manim/mobject/types/point_cloud_mobject.py:399` |
| `DotCloud`, `GlowDot`, `GlowDots`, `TrueDot` | None. Approximate `GlowDot` with concentric `Circle`s of decreasing fill opacity, or a `Dot` with `set_sheen` | GPU point sprites; no CE analogue. | `GL manimlib/mobject/types/dot_cloud.py:27,170,188` |
| `Checkmark`, `Exmark` | `Tex(r"\checkmark")` (needs LaTeX; `amssymb` is in the default preamble) or `Text("✓")` | | `GL manimlib/mobject/svg/drawings.py:80,85`; `CE manim/utils/tex_templates.py:24-50` |
| `SpeechBubble`, `ThoughtBubble`, `PiCreature`, `VideoIcon`, `Clock`, `Laptop` | None (3b1b's own drawings); build from `SVGMobject` or skip | License note: do not copy 3b1b's SVG assets or drawing code. | `GL manimlib/mobject/svg/drawings.py:266,296,463,497`; `V custom/characters/` |
| `AnimatedBoundary`, `TracedPath`, `TracingTail` | `AnimatedBoundary`, `TracedPath(traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None)` | `TracingTail` becomes `TracedPath(..., dissipating_time=...)`. | `GL manimlib/mobject/changing.py:18,98,151`; `CE manim/animation/changing.py:24,105,146-155` |

### Graphs, axes, number lines, matrices, numbers

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `Axes(x_range, y_range, width, height, axis_config)` | `Axes(x_range, y_range, x_length, y_length, axis_config, x_axis_config, y_axis_config, tips=True)` | CE draws arrow tips by default; 3b1b axes usually have none, so pass `tips=False`. CE default lengths are computed from `config.frame_width` at import time. | `GL manimlib/mobject/coordinate_systems.py:441-460`; `CE manim/mobject/graphing/coordinate_systems.py:1876,1931-1941` |
| `axes.get_graph(f, x_range=)` | `axes.plot(f, x_range=, color=)`; `plot_parametric_curve`, `plot_implicit_curve` | | `GL manimlib/mobject/coordinate_systems.py:184`; `CE manim/mobject/graphing/coordinate_systems.py:640,798,848` |
| `c2p`, `p2c`, `coords_to_point`, `i2gp`, `input_to_graph_point`, `get_graph_label` | Same | `get_graph_label` builds a `MathTex` (LaTeX). | `CE manim/mobject/graphing/coordinate_systems.py:158,163,213,219,1023,1103,1107` |
| `add_coordinate_labels()` | `add_coordinates()` | Uses `DecimalNumber`, hence LaTeX by default. | `GL manimlib/mobject/coordinate_systems.py:520`; `CE manim/mobject/graphing/coordinate_systems.py:390` |
| `get_v_line_to_graph(x, graph)`, `get_v_line`, `get_h_line` | `get_vertical_line(axes.i2gp(x, graph))`, `get_vertical_lines_to_graph`, `get_horizontal_line`, `get_lines_to_point` | | `GL manimlib/mobject/coordinate_systems.py:177-180,319`; `CE manim/mobject/graphing/coordinate_systems.py:533,567,599,1735` |
| `get_area_under_graph(graph, x_range)`, `get_riemann_rectangles` | `get_area(graph, x_range)`, `get_riemann_rectangles` | | `GL manimlib/mobject/coordinate_systems.py:363,417`; `CE manim/mobject/graphing/coordinate_systems.py:1189,1352` |
| `NumberPlane`, `ThreeDAxes`, `ComplexPlane`, `FunctionGraph`, `ParametricCurve`, `BarChart`, `UnitInterval` | `NumberPlane`, `ThreeDAxes`, `ComplexPlane`, `FunctionGraph`, `ParametricFunction`, `BarChart`, `UnitInterval` | | `CE manim/mobject/graphing/coordinate_systems.py:2414,2695,3380`; `CE manim/mobject/graphing/functions.py:28,188`; `CE manim/mobject/graphing/probability.py:223`; `CE manim/mobject/graphing/number_line.py:698` |
| `NumberLine(x_range, width, unit_size, include_numbers, ...)` | `NumberLine(x_range, length, unit_size, include_ticks, include_numbers, font_size=36, label_direction, label_constructor=MathTex, decimal_number_config, numbers_to_exclude, ...)`; `n2p`, `p2n`, `add_numbers`, `add_labels` | GL `width` is CE `length`. Labels are LaTeX unless `label_constructor` is swapped (see LaTeX section). | `GL manimlib/mobject/number_line.py:27`; `CE manim/mobject/graphing/number_line.py:35,141-171,359,443-447,526,581` |
| `TexMatrix`, `DecimalMatrix`, `MobjectMatrix`; `get_entries`, `get_rows`, `get_columns`, `get_brackets` | `Matrix(matrix, v_buff=0.8, h_buff=1.3, element_to_mobject=MathTex, left_bracket="[", right_bracket="]")`, `DecimalMatrix`, `IntegerMatrix`, `MobjectMatrix`; same accessors plus `set_column_colors`, `set_row_colors` | All default element constructors need LaTeX. | `GL manimlib/mobject/matrix.py:218,251,265`; `CE manim/mobject/matrix.py:75,165-180,284,311,341,363,416,441,467,513,550` |
| `DecimalNumber(number, num_decimal_places=2, include_sign, group_with_commas, show_ellipsis, unit, edge_to_fix=LEFT, font_size=48, text_config=)` (47 uses) | `DecimalNumber(number, num_decimal_places=2, mob_class=MathTex, include_sign, group_with_commas, show_ellipsis, unit, edge_to_fix=LEFT, font_size=48)`; `set_value`, `get_value`, `increment_value` | GL renders digits with `Text`; CE renders each digit with `MathTex` by default, so a changing number needs LaTeX. | `GL manimlib/mobject/numbers.py:34-53,208-227`; `CE manim/mobject/text/numbers.py:23,83-98,274-314` |
| `Integer` | Same; CE adds `Variable(value, label, var_type, num_decimal_places)` | | `CE manim/mobject/text/numbers.py:319,345` |
| `ValueTracker(value)`; `tracker.animate.set_value(x)` | Same; CE also supports `tracker += 1.5` style arithmetic | When a `ValueTracker` drives updaters, add it to the scene. | `GL manimlib/mobject/value_tracker.py:16`; `CE manim/mobject/value_tracker.py:21,62-64,78-195` |

### Images, SVG, 3D

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `ImageMobject(filename, height=)` (47 uses); files resolved under the configured `raster_images` directory | `ImageMobject(filename_or_array, scale_to_resolution=1080, invert=False, image_mode="RGBA")`; files resolved under `config.assets_dir` (default `./`) | Size the image afterwards with `.height = h` or `scale_to_fit_height`. Resampling algorithms `lanczos`, `box`, `hamming` were removed in 0.20.0. | `GL manimlib/default_config.yml:25`; `V custom_config.yml:6`; `CE manim/mobject/types/image_mobject.py:133,186-216`; `CE manim/utils/images.py:27-32`; `CE manim/_config/default.cfg:71-72`; `CE docs/source/changelog/0.20.0-changelog.md:14` |
| `SVGMobject(file_name, height=2.0, color=, ...)` (34 uses) | `SVGMobject(file_name, should_center=True, height=2, width=None, color, opacity, fill_color, fill_opacity, stroke_color, stroke_opacity, stroke_width, svg_default, path_string_config, use_svg_cache=True)` | Default height 2 in both. | `GL manimlib/mobject/svg/svg_mobject.py:57-60`; `CE manim/mobject/svg/svg_mobject.py:36,97-112` |
| `Surface`, `ParametricSurface(uv_func, u_range, v_range, resolution)` | `Surface(func, u_range=(0,1), v_range=(0,1), resolution=32, fill_color=BLUE_D, fill_opacity=1, checkerboard_colors=[...], stroke_width=0.5)` | CE surfaces are grids of `VMobject` pieces; `resolution` drives render cost. | `GL manimlib/mobject/types/surface.py:42,372`; `CE manim/mobject/three_d/three_dimensions.py:61,113-130` |
| `TexturedSurface(surface, image_file)` | Cairo: none. OpenGL: `OpenGLTexturedSurface` (usability unverified) | | `GL manimlib/mobject/types/surface.py:387`; `CE manim/mobject/opengl/opengl_surface.py:369` |
| `Cube`, `VCube`, `VPrism`, `Dodecahedron`, `Square3D` | `Cube(side_length, fill_opacity)`, `Prism`, `Dodecahedron` (and `Tetrahedron`, `Octahedron`, `Icosahedron`); `Square3D` approximated by `Square().set_shade_in_3d()`; CE adds `Sphere`, `Dot3D`, `Cone`, `Cylinder`, `Line3D`, `Arrow3D`, `Torus` | | `GL manimlib/mobject/three_dimensions.py:231-343`; `CE manim/mobject/three_d/three_dimensions.py:356,487,531,597,636,805,967,1206,1285`; `CE manim/mobject/three_d/polyhedra.py:30-375` |

### Constants, frame, colors

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `UP`, `DOWN`, `LEFT`, `RIGHT`, `IN`, `OUT`, `ORIGIN`, `UL`, `UR`, `DL`, `DR`, `X_AXIS`, `Y_AXIS`, `Z_AXIS` | Same | | `GL manimlib/constants.py:37-54`; `CE manim/constants.py:121-157` |
| `SMALL_BUFF` 0.1, `MED_SMALL_BUFF` 0.25, `MED_LARGE_BUFF` 0.5, `LARGE_BUFF` 1.0, `DEFAULT_MOBJECT_TO_EDGE_BUFF` 0.5, `DEFAULT_MOBJECT_TO_MOBJECT_BUFF` 0.25 | Same values; CE names end in `_BUFFER` for the two defaults | | `GL manimlib/default_config.yml:122-128`; `CE manim/constants.py:169-174` |
| `PI`, `TAU`, `DEG`, `DEGREES`, `RADIANS` | `PI`, `TAU`, `DEGREES` (no `DEG`, no `RADIANS`) | | `GL manimlib/constants.py:62-68`; `CE manim/constants.py:188-194` |
| `FRAME_WIDTH` (55 uses), `FRAME_HEIGHT`, `FRAME_X_RADIUS`, `FRAME_Y_RADIUS`, `TOP`, `BOTTOM`, `LEFT_SIDE`, `RIGHT_SIDE` | `config.frame_width`, `config.frame_height`, `config.frame_x_radius`, `config.frame_y_radius`, `config.top`, `config.bottom`, `config.left_side`, `config.right_side` | Frame is 8 units tall in both; width follows the pixel aspect ratio (16:9 gives 14.22). CE exposes these only on `config`. | `GL manimlib/constants.py:17-23,56-59`; `GL manimlib/default_config.yml:119`; `CE manim/_config/utils.py:1133-1188`; `CE docs/source/faq/general.md` ("default measurements") |
| `DEFAULT_STROKE_WIDTH` 4, `DEFAULT_FONT_SIZE` 48 (`Text`/`Tex` default `font_size=48`) | Same values | | `GL manimlib/default_config.yml:89`; `GL manimlib/mobject/svg/tex_mobject.py:41`; `CE manim/constants.py:183-184` |
| Palette `BLUE_A..E`, `TEAL_*`, `GREEN_*`, `YELLOW_*`, `GOLD_*`, `RED_*`, `MAROON_*`, `PURPLE_*`, `GREY_*`, `WHITE`, `BLACK`, `GREY_BROWN`, `DARK_BROWN`, `LIGHT_BROWN`, `PINK`, `LIGHT_PINK`, `ORANGE`, `PURE_RED`, `PURE_GREEN`, `PURE_BLUE`; shorthands `BLUE=BLUE_C`, `TEAL=TEAL_C`, `GREEN=GREEN_C`, `YELLOW=YELLOW_C`, `GOLD=GOLD_C`, `RED=RED_C`, `MAROON=MAROON_C`, `PURPLE=PURPLE_C`, `GREY=GREY_C` | Same names and hex values except two: GL `YELLOW_C`/`YELLOW` is `#FFFF00` while CE `YELLOW_C`/`YELLOW` is `#F7D96F` (CE `PURE_YELLOW` is `#FFFF00`); GL `BLUE_E` is `#1C758A` while CE `BLUE_E` is `#236B8E`. CE adds `GRAY_*` aliases, `PURE_CYAN`, `PURE_MAGENTA`, `LOGO_*`, and the large named palettes `XKCD`, `X11`, `SVGNAMES`, `BS381`, `AS2700`, `DVIPSNAMES`. GL `GREEN_SCREEN` has no CE name (use `PURE_GREEN`). | To reproduce 3b1b's highlight yellow use `PURE_YELLOW` or `"#FFFF00"`; define `BLUE_E = ManimColor("#1C758A")` locally if exact 3b1b blues matter. | `GL manimlib/default_config.yml:144-201`; `GL manimlib/constants.py:76-150`; `CE manim/utils/color/manim_colors.py:129-220`; `CE manim/utils/color/__init__.py` (package listing) |
| `MANIM_COLORS`, `COLORMAP_3B1B = [BLUE_E, GREEN, YELLOW, RED]` | None; write the list literal | | `GL manimlib/constants.py:137,150` |
| Background `#333333` (GL default) or `#000000` (3b1b config) | `background_color = BLACK` default; set via `-c`, `manim.cfg`, or `config.background_color` | | `GL manimlib/default_config.yml:61`; `V custom_config.yml:21`; `CE manim/_config/default.cfg:48-49` |
| `ManimColor` class, `interpolate_color`, `color_gradient`, `average_color`, `random_bright_color`, `rgba_to_color`, `color_to_rgb`, `interpolate_color_by_hsl` | `ManimColor`, `interpolate_color`, `color_gradient` (always returns a list), `average_color`, `random_bright_color`, `rgba_to_color`, `color_to_rgb`; no `interpolate_color_by_hsl` (use `HSV`) | `ManimColor.from_hex(hex=...)` became `from_hex(hex_str=...)` in 0.19.0. | `CE manim/utils/color/core.py:108,1091,1225-1481`; `CE docs/source/changelog/0.19.0-changelog.md:154`; `CE docs/source/changelog/0.19.1-changelog.md:53` |

### Rate functions and utilities

| ManimGL | ManimCE | Gotchas | Evidence |
| --- | --- | --- | --- |
| `linear`, `smooth`, `rush_into`, `rush_from`, `slow_into`, `double_smooth`, `there_and_back`, `there_and_back_with_pause`, `running_start`, `not_quite_there`, `wiggle`, `squish_rate_func`, `lingering`, `exponential_decay` | Same names; CE `smooth(t, inflection=10)`; CE adds `smoothstep`, `smootherstep`, `smoothererstep`, and the `ease_in_*`, `ease_out_*`, `ease_in_out_*` families | GL `overshoot` has no CE equivalent (write `lambda t: ...`). | `GL manimlib/utils/rate_functions.py:13-106`; `CE manim/utils/rate_functions.py:151-521` |
| `interpolate`, `inverse_interpolate`, `mid` | Same | | `CE manim/utils/bezier.py:1032,1119,1148` |
| `normalize`, `midpoint`, `rotate_vector`, `angle_of_vector`, `angle_between_vectors`, `compass_directions`, `cross`, `center_of_mass`, `rotation_matrix`, `z_to_vector`, `line_intersection`, `find_intersection` | Same | | `CE manim/utils/space_ops.py:74,185,259,299,315,340,364,463,529,545,566,610` |
| `get_norm(v)` (10 uses) | `np.linalg.norm(v)` | No CE helper. | `GL manimlib/utils/space_ops.py:42` |
| `sigmoid`, `clip` | Same | | `CE manim/utils/simple_functions.py:104,127` |
| `get_directories()`, `get_output_dir()` | `config.media_dir`, `config.assets_dir`, `config.video_dir`, ... | | `CE manim/_config/utils.py:1430,1669-1741` |

## ManimCE features relevant to teaching videos

### Sections and per-section outputs

- `Scene.next_section(name="unnamed", section_type=DefaultSectionType.NORMAL, skip_animations=False)` closes the current section and opens a new one; the first section is created automatically (`CE manim/scene/scene.py:378-388`; `CE manim/scene/section.py:14-36`).
- With `--save_sections` (or `save_sections = True` in `manim.cfg`) each section becomes its own MP4 under `{video_dir}/sections/`, named `<Scene>_<index>_<slug>.mp4`, plus `<Scene>.json` listing `name`, `type`, `video`, `codec_name`, `width`, `height`, `avg_frame_rate`, `duration`, `nb_frames` per section (`CE docs/source/tutorials/output_and_config.rst`, "Sections"; `CE manim/_config/default.cfg:24-25,76`; `CE manim/_config/output_plan.py:97-103`).
- A section with no `play` or `wait` is silently dropped; add `self.wait()` to keep it (`CE manim/scene/scene_file_writer.py:321-324`; same tutorial).
- `skip_animations=True` on a section fast-forwards it (useful while iterating on a later section).
- Design implication: one section per narration beat gives the pipeline a JSON index of clip durations to align against synthesized audio, without post-hoc cutting.

### Audio and subcaptions

- `Scene.add_sound(sound_file, time_offset=0, gain=None)` mixes an audio file at the current scene time (`CE manim/scene/scene.py:1768-1810`); audio is mixed into the final artifact separately from the silent cached segments (`CE docs/source/tutorials/output_and_config.rst`, "Output formats").
- `Scene.play(..., subcaption=..., subcaption_duration=..., subcaption_offset=...)` and `Scene.add_subcaption(content, duration, offset)` write an SRT subtitle track alongside the video (`CE manim/scene/scene.py:1188-1194,1726-1766`; `srt` is a hard dependency at `CE pyproject.toml:47`). This gives a narration transcript track for free.
- Since 0.19.0 CE bundles video encoding through `av` (PyAV) and no longer needs an external `ffmpeg` binary (`CE docs/source/changelog/0.19.0-changelog.md:13-16`; `CE pyproject.toml:26`). `pydub` is used for audio (`CE pyproject.toml:40`).
- The community `manim-voiceover` plugin adds `VoiceoverScene`, `set_speech_service(...)` and `with self.voiceover(text=...) as tracker: self.play(..., run_time=tracker.duration)` (`CE docs/source/guides/add_voiceovers.rst`). Latest release 0.4.0 (2026-06-14) depends only on `manim` at the top level and requires Python 3.11+ (PyPI metadata fetched 2026-10-25). It is optional: pre-generating narration audio, measuring its duration, and calling `add_sound` plus matching `run_time`/`wait` reproduces the same sync without the dependency.

### Configuration with manim.cfg

- Config precedence, lowest to highest: library `default.cfg`, user-wide `~/.config/manim/manim.cfg` (Linux and macOS), folder-wide `manim.cfg` next to the scene file (or `--config_file`), CLI flags, then programmatic `config.x = ...` (`CE docs/source/guides/configuration.rst`, "Order of operations").
- The folder-wide file is looked up next to the scene file, not in the working directory, and must be named `manim.cfg` (same guide).
- Keys under `[CLI]` are the long flag names. Keys useful for this pipeline, with defaults: `format = auto`, `save_sections = False`, `background_color = BLACK`, `media_dir = ./media`, `assets_dir = ./`, `renderer = cairo`, `frame_rate = 60`, `pixel_height = 1080`, `pixel_width = 1920` ("These now override the --quality option"), `max_files_cached = 100`, `disable_caching = False`, `tex_template =`, `plugins =`, `max_inflight_encoders = 1`, `encoder_queue_size = 8`, `verbosity = INFO`, `log_to_file = False` (`CE manim/_config/default.cfg:12-148`).
- Encoder settings live in `[video_encoder]` (`codec`, `pixel_format`, default `auto`) and `[video_encoder.options]` (for example `crf = 18`, `preset = slow`); CLI equivalents `--video-codec`, `--pixel-format`, `--encoder-option KEY=VALUE` (`CE manim/_config/default.cfg:198-207`; configuration guide).
- `manim cfg show` prints the resolved configuration; `manim render --help` is the authoritative flag list (configuration guide).
- Example folder-wide file for a narrated 1080p30 render:

```ini
[CLI]
pixel_width = 1920
pixel_height = 1080
frame_rate = 30
background_color = BLACK
format = mp4
save_sections = True
media_dir = ./media
assets_dir = ./assets
verbosity = WARNING

[video_encoder]
codec = libx264
pixel_format = yuv420p

[video_encoder.options]
crf = 18
preset = medium
```

### Quality flags and render-time implications

| Flag | Name | Resolution | FPS | Evidence |
| --- | --- | --- | --- | --- |
| `-ql` | `low_quality` | 854x480 | 15 | `CE manim/constants.py:231-236` |
| `-qm` | `medium_quality` | 1280x720 | 30 | `CE manim/constants.py:225-230` |
| `-qh` | `high_quality` | 1920x1080 | 60 | `CE manim/constants.py:219-224` |
| `-qp` | `production_quality` | 2560x1440 | 60 | `CE manim/constants.py:213-218` |
| `-qk` | `fourk_quality` | 3840x2160 | 60 | `CE manim/constants.py:207-212` |

- Frame count equals frame rate times scene seconds, so `-qh` renders twice as many frames as a 30 fps 1080p render; 3b1b renders at 30 fps (`V custom_config.yml:22`). For narrated videos, set `pixel_width`, `pixel_height` and `frame_rate = 30` in `manim.cfg` or pass `-r 1920,1080 --fps 30` (`CE manim/cli/render/render_options.py:198-212`; `CE manim/_config/default.cfg:125-128`).
- Iterate with `-ql` or `-s` (last frame only, equal to `--format=png`), and with `-n a,b` to render only animations `a` through `b` (`CE manim/_config/default.cfg:54-59`; output tutorial).
- No render timings were measured here (ManimCE is not installed in this container); the statements above follow from frame counts and the renderer architecture, not benchmarks.

### Output formats and file handling (0.22 rework)

- `--format` selects exactly one primary artifact: `auto` (MP4, or MOV when transparent; a scene with no `play`/`wait` yields a PNG with a warning), `mp4`, `mov`, `webm`, `gif`, `png` (last frame), `png-sequence`, `none` (`CE docs/source/tutorials/output_and_config.rst`, "Output formats"; `CE docs/source/changelog/0.22.0-changelog.md:14-27`).
- `-o NAME` names the primary artifact of a single scene; the format suffix is appended unless already present, and `-o` cannot be combined with `-a`/`--write_all` or several scene names (same tutorial).
- `-t`/`--transparent` with `--format=mp4` is rejected; transparent output goes to MOV, WebM or GIF (`CE docs/source/faq/general.md`, "transparent background").
- Output layout: `{media_dir}/videos/{module_name}/{quality}/<Scene>.mp4`, with `partial_movie_files/<Scene>/` holding cached segments and `partial_movie_file_list.txt` recording concatenation order; `sections/` beside it; images under `{media_dir}/images/{module_name}`; `Tex` and `texts` caches under `media_dir` (`CE manim/_config/default.cfg:66-80`; output tutorial).
- Removed in 0.22.0: `--write_to_movie`, `-g`/`--save_pngs`, `--custom_folders`, `--flush_cache` (replaced by `manim cache clear scene.py SceneName`), and the `[ffmpeg]` config section (now `[media]`/`config.media_loglevel`) (`CE docs/source/changelog/0.22.0-changelog.md:16-38,118-151`).

### Renderers: Cairo versus OpenGL

- Cairo is the default renderer (`renderer = cairo`, `CE manim/_config/default.cfg:83`); `--renderer=opengl` selects OpenGL (`CE manim/cli/render/render_options.py:250-258`).
- Only OpenGL advertises live preview (`-l`/`--live-preview`); with `--format=auto` live preview writes no file, so pass a concrete format to record (`CE docs/source/guides/configuration.rst`, "Command-line arguments"; `CE manim/renderer/protocol.py:11-14`). Since 0.22.0 the OpenGL renderer writes files by default like Cairo (`CE docs/source/changelog/0.22.0-changelog.md:25-26`).
- OpenGL mobject classes (`OpenGLMobject`, `OpenGLVMobject`, `OpenGLSurface`) are undocumented on the site and the two base-class hierarchies are "not fully compatible"; CE swaps classes at import time through the `ConvertToOpenGL` metaclass based on `config.renderer` (`CE docs/source/faq/opengl.md`; `CE docs/source/plugins.rst`, "renderer compatibility"; `CE manim/mobject/opengl/opengl_compatibility.py:17-29`).
- 0.21.0 sped up the Cairo renderer about 2.2x on animation-heavy scenes (`CE docs/source/changelog/0.21.0-changelog.md:25`). 0.22.0 introduced a `Manager` that coordinates the render lifecycle; regular scenes need no changes (`CE docs/source/changelog/0.22.0-changelog.md:45-64`; `CE manim/manager.py:31-67`).
- Recommendation for an unattended pipeline: Cairo. It is the default, fully documented path, needs no display, and `set_z_index`, `ThreeDScene.add_fixed_in_frame_mobjects` and the text stack are written against it.

### Caching and partial movie files

- Every `play` call is hashed (`get_hash_from_play_call`) and rendered to its own cached segment under `partial_movie_dir`; on re-render a matching hash reuses the segment (`CE manim/utils/caching.py:86-148`; `CE docs/source/guides/deep_dive.rst:818-829`).
- Cache keys include encoder settings, so changing codec options re-renders segments once (`CE docs/source/changelog/0.22.0-changelog.md:148-149`). 0.21.0 made NumPy arrays hash deterministically so changed image data invalidates correctly (`CE docs/source/changelog/0.21.0-changelog.md:44-46`).
- Large scenes trigger the warning "It looks like the scene contains a lot of sub-mobjects. Caching is sometimes not suited..." and suggest `--disable_caching`; `disable_caching_warning = True` silences it (`CE manim/utils/hashing.py:212-224`; `CE manim/_config/default.cfg:131-134`).
- `max_files_cached = 100` prunes old segments; `-1` keeps all (`CE manim/_config/default.cfg:130-131`; `CE manim/utils/caching.py:35-66`). `manim cache clear scene.py SceneName` clears a scene's segments (`CE manim/utils/caching.py:69`; output tutorial).
- `max_inflight_encoders` (default 1; "4 is a good value on typical hardware") overlaps encoding with rendering; `encoder_queue_size` bounds memory (`CE manim/_config/default.cfg:113-123`).

### Plugins

- A plugin is any package exposing an entry point in group `manim.plugins`; `manim plugins -l` lists them and `plugins = name1, name2` in `[CLI]` enables them (`CE manim/plugins/plugins_flags.py:13-21`; `CE manim/_config/default.cfg:146-148`; `CE docs/source/plugins.rst`).
- Since 0.18.1 plugins are not auto-injected into user namespaces; import them explicitly (`CE docs/source/plugins.rst`, `versionremoved` note). Missing configured plugins log a warning (`CE manim/plugins/__init__.py:16`).

### Text, MarkupText, Tex, MathTex, Typst and the LaTeX requirement

- Three text engines: Pango (`Text`, `MarkupText`, `Paragraph`), LaTeX (`Tex`, `MathTex`), Typst (`Typst`, `MathTypst`) (`CE docs/source/guides/using_text.rst`, opening section).
- LaTeX path: `TexTemplate` defaults to `tex_compiler="latex"` producing `.dvi`, converted with `dvisvgm` (at least 2.4, with PostScript specials) (`CE manim/utils/tex.py:30-47`; `CE manim/utils/tex_file_writing.py:118-165,226-260`; `CE docs/source/faq/general.md`, "PDF to SVG"). The default preamble is the 3b1b preamble (`babel`, `inputenc`, `fontenc`, `lmodern`, `amsmath`, `amssymb`, `dsfont`, `setspace`, `tipa`, `relsize`, `textcomp`, `mathrsfs`, `calligra`, `wasysym`, `ragged2e`, `physics`, `xcolor`, `microtype`) (`CE manim/utils/tex_templates.py:24-50,64`). The install docs list the LaTeX packages a minimal distribution needs (`CE docs/source/installation/uv.md:126-135`).
- What breaks without LaTeX (all raise during construction): `Tex`, `MathTex`, `SingleStringMathTex`, `BulletedList`, `Title`; `DecimalNumber`, `Integer`, `Variable` (digits are `MathTex`, `CE manim/mobject/text/numbers.py:87`); `Matrix`, `DecimalMatrix`, `IntegerMatrix` (`CE manim/mobject/matrix.py:174,489,534`); `NumberLine(include_numbers=True)`, `add_numbers`, `Axes.add_coordinates`, `get_graph_label` (`CE manim/mobject/graphing/number_line.py:164`; `CE manim/mobject/graphing/coordinate_systems.py:390,1107,3377`); `Brace.get_text`, `Brace.get_tex`, `BraceLabel`, `BraceText` (`CE manim/mobject/svg/brace.py:157,176,205,285`); `Vector.coordinate_label` (`CE manim/mobject/geometry/line.py:756`); `MathTable`.
- LaTeX failures surface as `ValueError: latex error converting to dvi` with the offending lines logged and hints for `inputenc` Unicode errors and missing `.sty` files (`CE manim/utils/tex_file_writing.py:181-224,285-360`).
- Lightweight alternatives: `Text`/`MarkupText` for prose and labels (Pango via `manimpango`, a hard dependency, `CE pyproject.toml:32`); `Typst`/`MathTypst` for formulas with `pip install "manim[typst]"` (compiler bundled, no TeX distribution; `CE docs/source/guides/using_text.rst`, "Text With Typst"; `CE manim/mobject/text/typst_mobject.py:1-13`); `Matrix(element_to_mobject=Text)` is accepted by the declared type `type[VMobject] | Callable` (`CE manim/mobject/matrix.py:174`); `DecimalNumber(mob_class=Text)` and `NumberLine(label_constructor=Text)` are type-hinted for `SingleStringMathTex`/`ManimTextLabel` and only plausibly work (unverified).
- Fonts: `Text(font=...)` must name an installed font (`manimpango.list_fonts()`); unknown fonts log `Font ... not in [...]` and fall back; `register_font(path)` loads a font file for the duration of a `with` block (`CE manim/mobject/text/text_mobject.py:480-490,1524`; using_text guide, "Using Fonts"). 0.22.0 ships a ManimPango with fixed kerning at small font sizes (`CE docs/source/changelog/0.22.0-changelog.md:66-72`).
- Text SVGs are cached under `text_dir` keyed by a hash; LaTeX SVGs under `tex_dir` (`CE manim/mobject/text/text_mobject.py:835-855`; `CE manim/utils/tex_file_writing.py:27-75`; `CE manim/_config/default.cfg:78-79`).

### 3D support

- `ThreeDScene` provides `set_camera_orientation`, `move_camera`, `begin_ambient_camera_rotation`, `begin_3dillusion_camera_rotation`, `add_fixed_in_frame_mobjects`, `add_fixed_orientation_mobjects` (`CE manim/scene/three_d_scene.py:31-437`).
- 3D mobjects: `ThreeDAxes`, `Surface`, `Sphere`, `Dot3D`, `Cube`, `Prism`, `Cone`, `Cylinder`, `Line3D`, `Arrow3D`, `Torus`, polyhedra (`CE manim/mobject/graphing/coordinate_systems.py:2414`; `CE manim/mobject/three_d/three_dimensions.py:49-1285`; `CE manim/mobject/three_d/polyhedra.py:30-375`). `VMobject.set_shade_in_3d` enables depth shading for flat shapes (`CE manim/mobject/types/vectorized_mobject.py:787`).
- With Cairo, surfaces are many small `VMobject` pieces sorted by depth; keep `resolution` modest and prefer 2.5D (rotating a `VGroup` in a `ThreeDScene`) for most teaching moments. Textured surfaces exist only on the OpenGL side (`CE manim/mobject/opengl/opengl_surface.py:369`).

## Pain points and gotchas for agent-written ManimCE code

### Common runtime errors and their causes

| Error text or symptom | Cause | Fix | Evidence |
| --- | --- | --- | --- |
| `TypeError: Passing Mobject methods to Scene.play is no longer supported. Use Mobject.animate instead.` | 2017-style `self.play(mob.shift, UP)` | `self.play(mob.animate.shift(UP))` | `CE manim/scene/scene.py:1020-1031` |
| `ValueError: Called Scene.play with no animations` | Empty unpack, e.g. `self.play(*[])` | Guard empty lists | `CE manim/scene/scene.py:1338` |
| `ValueError: Scene.play() has a run_time of 0 <= 0 seconds which Manim cannot render.` | Computed `run_time` from audio duration came out zero or negative | Clamp to at least `1/frame_rate` | `CE manim/scene/scene.py:1141-1168` |
| `Exception: Trying to restore without having saved` | `Restore(m)` without `m.save_state()` | Call `save_state()` first | `CE manim/mobject/mobject.py:2293` |
| `ValueError` from `MoveToTarget` | `generate_target()` not called | Call it, mutate `m.target`, then `MoveToTarget(m)` | `CE manim/animation/transform.py:432-440` |
| `TypeError` when adding to `VGroup` | `ImageMobject` or other non-`VMobject` member | Use `Group` | `CE manim/mobject/types/vectorized_mobject.py:2352-2362` |
| `TypeError: Animation only works on Mobjects`; `Object ... cannot be converted to an animation` | Passing a list of animations unexpanded, or a non-mobject | Unpack with `*` | `CE manim/animation/animation.py:187,581` |
| `ValueError: Animation arguments must be passed before accessing methods and can only be passed once` | `mob.animate.shift(UP)(run_time=2)` | `mob.animate(run_time=2).shift(UP)` | `CE manim/mobject/mobject.py:3573-3582` |
| `NotImplementedError: Method chaining is currently not supported for overridden animations` | Chaining after an `override_animate` method | Separate `play` calls | `CE manim/mobject/mobject.py:3588-3590` |
| `AttributeError: Camera object has no attribute 'frame'` style failures | Using `self.camera.frame` in a plain `Scene` | Subclass `MovingCameraScene` | `CE manim/camera/moving_camera.py:27,106`; `CE manim/scene/moving_camera_scene.py:104-121` |
| `AttributeError: ... object has no attribute 'set_backstroke'` (or `get_grid`, `replicate`, `fix_in_frame`, `set_max_width`, `reorient`) | GL-only API | Use the translation rows above | `CE manim/mobject/mobject.py:904` |
| `ValueError: latex error converting to dvi` | LaTeX missing, a package missing, or a bad formula | Install TeX Live with the listed packages, or switch to `Text`/`Typst` | `CE manim/utils/tex_file_writing.py:217-224,305-310` |
| `dvisvgm` errors or empty glyphs | `dvisvgm` older than 2.4 or without PostScript support | Update `dvisvgm`; see FAQ | `CE manim/utils/tex_file_writing.py:258-260`; `CE docs/source/faq/general.md` |
| `Font ... not in [...]` warning and wrong font | Font not installed for Pango | Install font or `register_font` | `CE manim/mobject/text/text_mobject.py:480-490,1524` |
| Updaters do nothing | Mobject (or driving `ValueTracker`) not added to the scene, or the mobject is being animated (`suspend_mobject_updating=True`) | `self.add(...)`; pass `suspend_mobject_updating=False` | `CE manim/scene/scene.py:409-420`; `CE manim/animation/animation.py:108`; `CE manim/mobject/value_tracker.py:62-64` |
| Section missing from the JSON index | Section contained no `play`/`wait` | Add `self.wait()` | `CE manim/scene/scene_file_writer.py:321-324` |
| `-o` rejected | Combined with `-a` or several scenes | Name per scene, or rely on default names | `CE docs/source/tutorials/output_and_config.rst` |
| Transparent MP4 rejected | `-t` with `--format=mp4` | Use `mov`/`webm`/`gif` | `CE docs/source/faq/general.md` |
| "There are no scenes inside that module" | `manim` executable belongs to ManimGL, or `construct` misspelled | `manimce`/`python -m manim`; check `construct` | `CE docs/source/faq/general.md` |
| `ValueError: Too few rows and columns to fit all ...` | `arrange_in_grid(rows, cols)` too small | Fix counts | `CE manim/mobject/mobject.py:2901` |
| `ValueError: Alpha ... not between 0 and 1` | `point_from_proportion` out of range | Clamp alpha | `CE manim/mobject/types/vectorized_mobject.py:1660` |
| `ValueError: A static Wait animation cannot have a stop condition` | `wait(stop_condition=..., frozen_frame=True)` | Drop one of them | `CE manim/animation/animation.py:616` |
| `TypeError: Expected all inputs for parameter mobjects to be a Mobjects` | `SurroundingRectangle(point)` with a non-mobject | Pass mobjects | `CE manim/mobject/geometry/shape_matchers.py:59-62` |
| Python version error on install | CE requires Python 3.11+ (since 0.19.2) | Use 3.11-3.14 | `CE pyproject.toml:23`; `CE docs/source/changelog/0.19.2-changelog.md:14` |

### API changes across recent versions

| Version | Change that affects generated code | Evidence |
| --- | --- | --- |
| 0.19.0 | External `ffmpeg` no longer required (PyAV). Python 3.13 supported. `Scene.next_section(type=)` renamed to `section_type=`. `ManimColor.from_hex(hex=)` renamed to `hex_str=`. `Sector` lost `inner_radius`/`outer_radius`. `turn_animation_into_updater(delay=)` added. `Code` mobject rewritten (0.19.1 refers to the "new `Code` mobject"). | `CE docs/source/changelog/0.19.0-changelog.md:13-16,129,154-158,211`; `CE docs/source/changelog/0.19.1-changelog.md:24` |
| 0.19.1 | `always_redraw` optimized (less copying in `become`); `color_gradient` always returns a list; `SceneFileWriter.save_final_image` renamed `save_image`. | `CE docs/source/changelog/0.19.1-changelog.md:48,53,129` |
| 0.19.2 | Minimum Python 3.11; Python 3.14 supported. | `CE docs/source/changelog/0.19.2-changelog.md:14` |
| 0.20.0 | `ImageMobject` resampling algorithms `lanczos`/`antialias`, `box`, `hamming` removed. `MathTex` rewritten for robust splitting. `mob.always.method(...)` updater builder added. | `CE docs/source/changelog/0.20.0-changelog.md:14-26` |
| 0.20.1 | `MathTex` double-brace splitting no longer fires on natural `}}`. | `CE docs/source/changelog/0.20.1-changelog.md:18` |
| 0.21.0 | Cairo renderer 2.2x faster with a pixel-conversion behavior change; `Typst`/`MathTypst` added (`TypstMath` renamed `MathTypst`); NumPy arrays hashed deterministically in cache keys; `MathTex` handles multiline strings. | `CE docs/source/changelog/0.21.0-changelog.md:25-46,89,119` |
| 0.22.0 | Unified `--format`; `--write_to_movie`, `-g`/`--save_pngs`, `--custom_folders`, `--flush_cache` removed; `manim cache clear`; `[video_encoder]` config; `Manager` object (`Scene.render`, `play`, `next_section` route through it); OpenGL writes files by default; section videos include the section name; `[ffmpeg]` config section replaced by `[media]`. | `CE docs/source/changelog/0.22.0-changelog.md:14-38,45-64,75-151` |

CE currently has no `@deprecated`-decorated APIs left in the tree (a grep for
`@deprecated(` and `deprecated_params(` outside `CE manim/utils/deprecation.py`
returns nothing), so the main hazard is version skew in training data, not
live deprecation warnings. Pin `manim==0.22.0` (or newer after checking the
changelog) in the skill's environment assumptions.

### Performance traps

- Default 60 fps at `-qh`/`-qp`/`-qk` doubles frame counts versus 3b1b's 30 fps; set `frame_rate = 30` explicitly (`CE manim/constants.py:207-224`; `V custom_config.yml:22`).
- Hashing very large mobject trees per `play` call is slow and warns; disable caching for one-shot renders with `--disable_caching` (`CE manim/utils/hashing.py:212-224`).
- `always_redraw` reconstructs its mobject every frame; prefer `add_updater` with in-place mutation (`move_to`, `set_value`, `put_start_and_end_on`) for anything larger than a label (`CE manim/animation/updaters/mobject_update_utils.py:67-111`).
- Every distinct `Tex`/`MathTex` string compiles LaTeX on first use (then cached under `tex_dir`); hundreds of unique formulas add seconds each on a cold cache (`CE manim/utils/tex_file_writing.py:27-75`).
- `Write` and `Create` on long `Text`/`Tex` iterate over every glyph; the auto run time is 1-2 s, so very long text just reveals faster, but each glyph is a submobject that costs rendering and hashing (`CE manim/animation/creation.py:344-354`).
- Cairo 3D `Surface(resolution=32)` creates about a thousand pieces; keep resolution small and scenes short (`CE manim/mobject/three_d/three_dimensions.py:113-130`).
- Large `ImageMobject` pixel arrays are composited in software; downscale source images and use `scale_to_resolution` sensibly (`CE manim/mobject/types/image_mobject.py:186-216`).
- Encoding can overlap rendering with `max_inflight_encoders = 4` on multi-core machines (`CE manim/_config/default.cfg:113-118`).
- During iteration use `-ql`, `-s`, `-n a,b`, and `next_section(skip_animations=True)` to avoid re-rendering finished parts.

## ManimCE idioms for 3b1b-style moves

All snippets are original ManimCE code, not ports of 3b1b scenes.

1. Focus on one element and dim the rest:

   ```python
   others = VGroup(*[m for m in diagram if m is not focus])
   self.play(
       others.animate.set_opacity(0.2),
       focus.animate.set_color(PURE_YELLOW),
   )
   self.play(Circumscribe(focus, time_width=0.4), run_time=1.2)
   # alternative: a dark overlay under the focus element
   veil = FullScreenRectangle(fill_color=BLACK, fill_opacity=0.7, stroke_width=0)
   focus.set_z_index(1)
   self.play(FadeIn(veil))
   ```

   Evidence: `CE manim/mobject/types/vectorized_mobject.py:478`; `CE manim/animation/indication.py:571`; `CE manim/mobject/frame.py:38`; `CE manim/mobject/mobject.py:3489`.

2. Morph a formula into a diagram (and back):

   ```python
   eq1 = MathTex(r"{{ w }} \cdot {{ x }} + {{ b }}")
   eq2 = MathTex(r"\sigma \left( {{ w }} \cdot {{ x }} + {{ b }} \right)")
   self.play(TransformMatchingTex(eq1, eq2, path_arc=30 * DEGREES))
   w_part = eq2.get_part_by_tex("w")
   self.play(TransformFromCopy(w_part, weight_label))   # formula term flies to the diagram
   self.play(FadeTransform(eq2, network_diagram))       # whole-formula crossfade
   ```

   Evidence: `CE manim/mobject/text/tex_mobject.py:239-258,543`; `CE manim/animation/transform_matching_parts.py:237`; `CE manim/animation/transform.py:307,812`.

3. Trace a path:

   ```python
   dot = Dot(color=YELLOW)
   trail = TracedPath(dot.get_center, stroke_color=YELLOW, stroke_width=3, dissipating_time=1.0)
   self.add(trail, dot)
   self.play(MoveAlongPath(dot, curve), run_time=4, rate_func=linear)
   self.play(ShowPassingFlash(curve.copy().set_stroke(WHITE, 6), time_width=0.5))
   ```

   Evidence: `CE manim/animation/changing.py:105,146-155`; `CE manim/animation/movement.py:173`; `CE manim/animation/indication.py:274`.

4. Animate a number with a tracker:

   ```python
   tracker = ValueTracker(0)
   number = DecimalNumber(0, num_decimal_places=2).add_updater(
       lambda d: d.set_value(tracker.get_value())
   )
   self.add(tracker, number)
   self.play(tracker.animate.set_value(0.73), run_time=2)
   # or, without a tracker:
   self.play(ChangeDecimalToValue(number, 0.73))
   ```

   Evidence: `CE manim/mobject/value_tracker.py:21,62-64`; `CE manim/mobject/text/numbers.py:274`; `CE manim/animation/numbers.py:74`.

5. Camera zoom and pan (2D):

   ```python
   class Zoom(MovingCameraScene):
       def construct(self):
           self.camera.frame.save_state()
           self.play(self.camera.frame.animate.scale(0.4).move_to(neuron))
           self.wait()
           self.play(Restore(self.camera.frame))
   ```

   Evidence: `CE manim/scene/moving_camera_scene.py:17-64,104-121`.

6. Staggered reveal:

   ```python
   self.play(LaggedStartMap(FadeIn, layer_neurons, shift=0.3 * UP, lag_ratio=0.05))
   self.play(LaggedStart(*[GrowArrow(a) for a in edges], lag_ratio=0.02, run_time=2))
   self.play(Write(title))
   ```

   Evidence: `CE manim/animation/composition.py:297,351`; `CE manim/animation/growing.py:176`; `CE manim/animation/creation.py:291`.

7. Keep labels attached:

   ```python
   label = Text("weight", font_size=24).add_updater(lambda m: m.next_to(edge, UP, buff=0.1))
   connector = always_redraw(lambda: Line(a.get_center(), b.get_center(), color=GREY_B))
   brace = Brace(group, DOWN)
   caption = Text("inputs", font_size=28).next_to(brace, DOWN)  # LaTeX-free; brace.get_text needs LaTeX
   ```

   Evidence: `CE manim/mobject/mobject.py:1148`; `CE manim/animation/updaters/mobject_update_utils.py:67`; `CE manim/mobject/svg/brace.py:33,157`.

8. Highlight sweep and callouts:

   ```python
   box = SurroundingRectangle(term, color=PURE_YELLOW, buff=0.08, corner_radius=0.05)
   self.play(Create(box))
   self.play(Indicate(term))
   self.play(Flash(dot.get_center(), color=PURE_YELLOW))
   text.set_stroke(BLACK, 5, background=True)   # readable text over busy backgrounds
   ```

   Evidence: `CE manim/mobject/geometry/shape_matchers.py:26`; `CE manim/animation/indication.py:125,171`; `CE manim/mobject/types/vectorized_mobject.py:332-345`.

9. Narration beats as sections with audio:

   ```python
   self.next_section("beat-01-intro")
   self.add_sound("audio/beat-01.wav")
   self.play(Write(title), run_time=2.0, subcaption="Let us start with one neuron.")
   self.wait(beat_duration - 2.0)
   self.next_section("beat-02-weights")
   ```

   Render with `manim --save_sections scene.py Lesson` and read `media/videos/scene/1080p30/sections/Lesson.json` for per-beat durations. Evidence: `CE manim/scene/scene.py:378-388,1188-1194,1768`; `CE docs/source/tutorials/output_and_config.rst`.

10. Delayed sub-animation (the GL `time_span` pattern):

    ```python
    self.play(
        AnimationGroup(
            FadeIn(a),
            Succession(Wait(0.5), FadeIn(b)),
            Succession(Wait(1.0), FadeIn(c)),
        ),
        run_time=2,
    )
    ```

    Evidence: `CE manim/animation/composition.py:30,198`; `CE manim/animation/animation.py:584`.

11. 3D orbit with a fixed title:

    ```python
    class Orbit(ThreeDScene):
        def construct(self):
            axes = ThreeDAxes()
            title = Text("Loss surface").to_corner(UL)
            self.add_fixed_in_frame_mobjects(title)
            self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.9)
            self.add(axes, surface)
            self.begin_ambient_camera_rotation(rate=0.1)
            self.wait(6)
    ```

    Evidence: `CE manim/scene/three_d_scene.py:55-140,357`.

12. Layering and foregrounds: add mobjects in paint order, call `self.bring_to_front(mob)` for one-offs, and reserve `set_z_index` for persistent overlays such as veils and HUD labels (`CE manim/scene/scene.py:870-889`; `CE manim/mobject/mobject.py:3489-3530`; `CE manim/camera/camera.py:91,108`).

## Unverified or blocked items

- The ManimCE documentation website is blocked here; all documentation citations point at the docs source in the clone, which is the same content the site is built from.
- No ManimCE or ManimGL was installed or executed in this container, so signatures and behaviors come from reading source; no render was run and no timing was measured.
- The ManimGL clone (2026-09-09) is far ahead of the last PyPI release 1.7.2 (2024-12-13) under the same version string; the series code targets the clone's APIs.
- Whether `DecimalNumber(mob_class=Text)` and `NumberLine(label_constructor=Text)` work is plausible from the code path but untested.
- Exact equivalence of GL `reorient(theta, phi)` angle conventions with CE `set_camera_orientation(phi, theta)` beyond the degrees-to-radians change is unverified.
- `FadeIn(target_position=..., scale=...)` as a stand-in for GL `FadeInFromPoint` is a visual approximation.
- `OpenGLTexturedSurface` usability in a non-interactive render is unverified.
- The kit's `ultracode` skill named in the user request was removed from the kit (`/home/user/.agents/CHANGELOG.md:57-59`) and could not be used; this map was produced with the task's own method instead.
