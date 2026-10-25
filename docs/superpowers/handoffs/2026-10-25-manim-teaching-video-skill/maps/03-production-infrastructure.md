# 3Blue1Brown production infrastructure and workflow map

This map describes how Grant Sanderson's `3b1b/videos` repository is configured,
what reusable production components it carries, how he iterates on a scene, how a
video is assembled from rendered scenes, and what the code reveals about how
narration and animation are coordinated. Every claim is tied to a file and line
range; anything that could not be verified from a local source is marked
"unverified". The closing sections translate each finding into requirements for an
agent-driven ManimCE pipeline.

## Sources and citation conventions

Local read-only sources:

- `/home/user/3b1b/videos` at commit `306a1346` (2026-09-29). Canonical page:
  <https://github.com/3b1b/videos>.
- `/home/user/3b1b/manim` (ManimGL, the renderer the repo targets) at commit
  `fafa083a`, version `1.7.2` per `setup.cfg` line 3. Canonical page:
  <https://github.com/3b1b/manim>.
- `/home/user/ManimCommunity/manim` (ManimCE, our target) at commit `bb380986`,
  version `0.22.0` per `pyproject.toml` line 3. Canonical page:
  <https://github.com/ManimCommunity/manim>.

Citations are written as `path:Lstart-Lend`, relative to the repository root
named in the surrounding text. `docs.manim.community`, `3b1b.github.io` and
YouTube are blocked in this container, so every ManimGL and ManimCE behavior
below was read from library source rather than rendered documentation. The
README links a workflow video on YouTube (`README.md:L17`); its content is
unverified here.

## 1. Rendering configuration

### 1.1 Effective settings

`custom_config.yml` at the repo root is the only configuration file; ManimGL
merges it over `manimlib/default_config.yml` (the default file says so in its
header, `manimlib/default_config.yml:L1-9`). The table lists the values a 3b1b
render actually uses, the ManimGL default it overrides, and the ManimCE default
the skill will start from.

| Setting | 3b1b value (`custom_config.yml`) | ManimGL default (`manimlib/default_config.yml`) | ManimCE default |
| --- | --- | --- | --- |
| Resolution | `(3840, 2160)` L20 | `(1920, 1080)` L60 | `1920x1080` (`manim/_config/default.cfg:L127-128`); `-qk` preset is 3840x2160 (`manim/constants.py:L207-212`) |
| Frame rate | `30` L22 | `30` L62 | `60` (`default.cfg:L126`); `-qk` and `-qh` presets are 60 fps, `-qm` 30, `-ql` 15 (`constants.py:L206-236`) |
| Background | `"#000000"` L21, opacity `1.0` L23 | `"#333333"` L61 | `BLACK` (`default.cfg:L49`) |
| Saturation post-filter | `1.5` L25 | `1.0` L70 | none in `default.cfg` (unverified whether any CE option exists) |
| Video codec / pixel format | inherited | `libx264`, `yuv420p` L68-69 | `auto` (`default.cfg:L198-202`) |
| Text font | `"CMU Serif"` L27 | `"Consolas"` L102 | `""`, Pango default (`manim/mobject/text/text_mobject.py:L456`) |
| Text alignment | `"CENTER"` L28 | `"LEFT"` L103 | not configured globally |
| Tex template | `"default"` L30 | `"default"` L97 | empty, falls back to `TexTemplate()` (`default.cfg:L144`) |
| Frame height | inherited | `8.0` manim units L119 | 8 units (unverified from CE source here) |
| Default `wait()` | inherited | `1.0` s L85 | `DEFAULT_WAIT_TIME` (unverified value) |
| Default stroke width | inherited | `4.0` L89 | not checked |
| Window-less output dir | Dropbox mirror, see 1.4 | `videos/` under `directories.base` L20-23 | `./media/videos/{module_name}/{quality}` (`default.cfg:L66-75`) |

Two facts matter for the skill. First, 3b1b's resolution and frame rate are 4K at
30 fps, not 60 fps: `CLAUDE.md:L65` restates this. Second, the background is pure
black, which happens to be ManimCE's default too, whereas ManimGL's own default
is dark grey. The saturation filter is applied by ffmpeg at encode time
(`manimlib/scene/scene_file_writer.py:L227-233` builds `-vf eq=saturation=...`),
so raw ManimGL colors are 50% more saturated in the finished videos than in the
source constants. The color palette itself (`BLUE_E` through `PURE_BLUE`) is
defined in `manimlib/default_config.yml:L144-201`.

### 1.2 Configuration layering inside a scene

`Scene.__init__` merges three layers for the camera: the global
`manim_config.camera`, the class attribute `default_camera_config`, and the
`camera_config` constructor argument (`manimlib/scene/scene.py:L90-94`); the
file writer is layered the same way (`L95-99`). When a preview window exists the
frame rate is forced to 30 (`L102-105`). The scene exposes its camera frame as
`self.frame` (`L113`), orients it from `default_frame_orientation` (`L62`,
`L114`), and seeds `random` and `numpy` when `random_seed` is set (`L140-142`).
`custom/banner.py:L20` sets a class attribute named `camera_config` rather than
`default_camera_config`; under the current `Scene.__init__` that attribute is
shadowed by the instance value, so the banner's 2560x1440 override is probably
inert (unverified by running it).

### 1.3 Text and Tex

`Text` uses CMU Serif, centered (`custom_config.yml:L26-28`). `Tex` uses the
`default` template from `manimlib/tex_templates.yml:L3-28`: compiler `latex`,
and a preamble loading `babel`, `inputenc`, `fontenc`, `amsmath`, `amssymb`,
`dsfont`, `setspace`, `tipa`, `relsize`, `textcomp`, `mathrsfs`, `calligra`,
`wasysym`, `ragged2e`, `physics`, `xcolor`, `microtype`, `pifont`, disabling
ligatures, setting `\linespread{1}`, and declaring a shorter `\minus` symbol
(`L27-28`). That `\minus` macro is used in recent scenes, for example
`_2025/laplace/supplements.py:L12`. The README's install section names the
TeX Live packages this preamble needs: `texlive`, `texlive-latex-extra`,
`texlive-fonts-extra`, `texlive-science` (`README.md:L56-59`).

ManimCE's `TexTemplate` default preamble is only `babel`, `amsmath`, `amssymb`
(`manim/utils/tex.py:L21-23`), with `\documentclass[preview]{standalone}`
(`L47`), compiler `latex` (`L36`) and `.dvi` output (`L44`). The skill therefore
needs its own `TexTemplate` that adds at least `dsfont`, `mathrsfs`, `physics`
and `xcolor` plus the `\minus` declaration, or the ported idioms will fail to
compile.

### 1.4 Output directories, file naming and assets

`directories.mirror_module_path: True` with `removed_mirror_prefix` and a
Dropbox `base` (`custom_config.yml:L1-4`) means a render of
`_2025/laplace/supplements.py` lands in a Dropbox folder that mirrors the source
path. The Sublime helper `OpenMirroredDirectory` shows the mapping concretely: it
replaces the source root with the Dropbox `videos` root and strips underscores
from the path (`sublime_custom_commands/manim_plugins.py:L233-245`). Asset
subdirectories are `images/raster`, `images/vector`, `images/models`,
`images/pi_creature/svg` and `manim_downloads` (`custom_config.yml:L5-10`);
defaults also define `sounds`, `data` and `latex_cache` subdirectories
(`manimlib/default_config.yml:L21-35`), read through `get_directories()`
(`manimlib/utils/directories.py:L13-14`) and helpers such as `get_output_dir()`
(`L29-30`) and `get_sound_dir()` (`L45-46`).

None of these assets are in the public repo: a search for `*.svg` and `*.png`
under `/home/user/3b1b/videos` finds zero files. Scenes reference them by bare
name (`ImageMobject("AttentionPaper")`, `_2024/transformers/supplements.py:L844`)
or by absolute Dropbox path (`_2025/laplace/supplements.py:L440`,
`_2025/cosmic_distance/part2.py:L825`). Data for the transformer series is
resolved relative to the output directory (`_2024/transformers/helpers.py:L9`).

Output naming in ManimGL: the movie file is `<SceneClassName>.mp4`, with
`_<start>` and `_<end>` suffixes when `-n` limits the animation range
(`manimlib/scene/scene_file_writer.py:L108-120`, extension `L36`). With
`--subdivide` each `play()` becomes `NNNNN.mp4` inside a directory named after
the scene (`L126-128`; flag at `manimlib/config.py:L147-152`). Recorded
checkpoint snippets go to an `inserts/` sibling directory as
`<Scene>_<index>.mp4` (`L258-263`). Frames are piped to ffmpeg as raw RGBA with
`-an` (`L207-240`); if `add_sound` was called, a `.wav` is exported and muxed as
AAC 320k in a second ffmpeg pass (`L317-346`).

ManimCE's layout is `media_dir` (default `./media`), `video_dir
= {media_dir}/videos/{module_name}/{quality}`, `sections_dir
= {video_dir}/sections`, `partial_movie_dir
= {video_dir}/partial_movie_files/{scene_name}` (`manim/_config/default.cfg:
L66-80`). Section videos are named `{stem}_{index:04}_{slug}.mp4`
(`manim/_config/output_plan.py:L91-100`, slug rules `L103-108`), and a JSON
index of sections is written beside them
(`manim/scene/scene_file_writer.py:L966-984`). Config files are layered
library-wide, user-wide (`~/.config/manim/manim.cfg`) and folder-wide
(`./manim.cfg`) (`manim/_config/utils.py:L46-85`).

### 1.5 Camera and frame idioms

The repo treats the camera frame as a first-class mobject. In `_2025` and
`_2026` there are 248 uses of `self.frame`, 101 of `frame.reorient(...)`, 117
of `fix_in_frame` and 29 of `self.camera.light_source` (counts from `grep -rF`
over `*.py`). `reorient(theta, phi, gamma, center, height)` sets a 3D camera
pose in one call (`_2024/transformers/attention.py:L1422-1423`,
`_2026/cross_entropy/transformer_render.py:L413`); `fix_in_frame()` pins HUD
elements such as titles and panels while the frame moves
(`_2025/laplace/supplements.py:L7`, `L21-22`); `set_field_of_view` narrows
perspective (`attention.py:L1422`, `_2025/colliding_blocks_v2/blocks.py:L112`).

ManimCE equivalents: `MovingCameraScene` exposes `self.camera.frame` for 2D
pans and zooms (`manim/scene/moving_camera_scene.py:L17-18` docstring example);
`ThreeDScene.add_fixed_in_frame_mobjects` pins HUD elements under the Cairo
renderer (`manim/scene/three_d_scene.py:L357-372`); `fix_in_frame` exists only on
OpenGL mobjects (`manim/mobject/opengl/opengl_mobject.py:L2933`). The pattern
library must translate `reorient` into `set_camera_orientation` plus
`move_camera` and keep 2D scenes on `MovingCameraScene`.

## 2. Reusable production components

Everything a scene file needs arrives through one import line,
`from manim_imports_ext import *` (`custom_config.yml:L12` sets it as the
`universal_import_line`; 370 of the repo's `.py` files start with it, 4 use
`from manimlib import *`). `manim_imports_ext.py:L1-14` re-exports `manimlib`,
the legacy `old_tex_mobject` module, and every module under `custom/`. The
components are listed below with what they provide and how scenes consume them.
Per the project's license decision, the skill derives principles from these and
ships original ManimCE code; nothing here is to be copied.

### 2.1 Backdrops (`custom/backdrops.py`)

- `Spotlight` (`L14-31`): a title at the top, a full-screen rectangle, and a
  6-unit-tall black `ScreenRectangle` at the bottom wrapped in an
  `AnimatedBoundary`, held for 16 seconds. It is a frame for footage dropped in
  later by the editor.
- `VideoWrapper` (`L34-70`): the same idea with configurable `title`,
  `screen_height = 6.25`, `wait_time = 32`, and a boundary `cycle_rate` of 0.25;
  the title is written with `Write` and sized to the screen width (`L61-68`).

Both are placeholders whose black rectangle is replaced in post-production, which
is why they only `wait`. The agent pipeline has no editor, so the equivalent is
an in-scene "picture in picture" region drawn directly, or no wrapper at all.

### 2.2 End screens (`custom/end_screen.py`)

- `PatreonEndScreen(InteractiveScene)` (`L44-206`): title "Clicky Stuffs"
  (`L45`), a thanks message naming `3b1b.co/support` (`L56-59`), a 20-second
  scroll (`L60`), two Pi creatures that blink randomly (`L83-91`, `L178-186`),
  and a patron list read from `top_patrons.txt`, `hardcoded_patrons.txt` and a
  `patron_name_replacements.json` substitution map in the `data` directory
  (`L114-138`). Names are laid out with `arrange_in_grid` in 4 columns
  (`L167-171`) and scrolled by shifting the camera frame while everything else is
  `fix_in_frame`'d (`L188-206`).
- `SideScrollEndScreen(PatreonEndScreen)` (`L209-351`): a 2/5 + 3/5 split
  (`L257-263`), outlines where YouTube places the next-video, channel and link
  elements (`L268-281`), a `3b1b.co/support` link text (`L230`, `L284-287`), a
  Randolph with a speech bubble about early views (`L289-321`), and a 21-second
  scroll (`L214`).

Every recent project defines its own end screen by subclassing with `pass`
(`_2026/cross_entropy/supplements.py:L1069-1070`,
`_2024/transformers/supplements.py:L834-835`); 2024-2026 contain 10
`SideScrollEndScreen` and 7 `PatreonEndScreen` subclasses (class-base census).
The data files are not public. For a generated teaching video the end screen is
optional; what transfers is the pattern "scroll by moving the frame while the
HUD stays fixed".

### 2.3 Logo (`custom/logo.py`)

`Logo(VMobject)` (`L28-207`) builds the eye procedurally: two annular sectors
(blue `#74C0E3`, brown `#8C6239`, `L31-32`), four layers of 28 spikes with
graded blues and browns (`L33-47`, `L80-157`), and a black pupil (`L159-169`).
`LogoGenerationTemplate` (`L210-234`) shifts the frame down, writes the channel
name scaled 2.5x under the logo and runs subclass-provided animations over 3
seconds; five intro variants follow (`L237-478`). The logo is brand identity and
must not be reproduced.

### 2.4 Opening quote (`custom/opening_quote.py`)

`OpeningQuote(Scene)` (`L9-66`): quote words fade in with `lag_ratio = 0.5`,
linear rate, over 5 seconds (`L14-18`), hold 2 seconds, then the author is
written in yellow over 3 seconds (`L28-31`, `L62-66`); highlighted terms are
colored by `set_color_by_tex` (`L55-56`), width capped to the frame (`L58-59`).
Recent videos reproduce this with `InteractiveScene` subclasses instead
(`_2026/2025_P6/p6.py:L4532`, `L4586`, `L4599`). The pedagogical pattern (quote
first, author second, slow linear fade) is reusable as an original scene.

### 2.5 Banner (`custom/banner.py`)

`Banner(Scene)` (`L19-100`) is channel art: a faded `NumberPlane` background
(`L33-42`), four Pi creatures of graded blues plus a brown Mortimer (`L76-82`),
a message or "Next video on <date>" text with a yellow date (`L84-94`), and an
optional supporter note (`L96-100`). It is not part of a video and not relevant
to the skill beyond showing the house color grading.

### 2.6 Pi creatures (`custom/characters/`)

- `pi_creature.py`: `PiCreature(SVGMobject)` (`L41-296`) loads
  `<mode>.svg` from the `pi_creature_images` directory and falls back to
  `plain.svg` with a warning (`L83-94`), extracts eyes, body and mouth from the
  Figma export by index (`L96-107`), redraws pupils as circles (`L109-131`), and
  smooths mode changes by inserting 100 curves into the body (`L81`). Behaviors:
  `change_mode` (`L147-158`), `look` and `look_at` (`L163-185`), `blink`
  (`L198-207`), `get_bubble` (`L209-213`), and animation builders `change`,
  `says`, `thinks`, `replace_bubble`, `debubble` (`L247-296`). Named characters
  are `Randolph` (default blue), `Mortimer` (grey-brown, flipped to face left,
  `L303-311`), `Mathematician`, `BabyPiCreature`, `TauCreature` (`L314-357`).
- `pi_creature_animations.py`: `Blink` as a squished `there_and_back`
  (`L23-30`); `PiCreatureBubbleIntroduction` runs a mode change, a
  `DrawBorderThenFill` of the bubble and a `Write` of its content together
  (`L33-64`); `RemovePiCreatureBubble` (`L84-110`).
- `pi_creature_scene.py`: `PiCreatureScene(InteractiveScene)` (`L37-245`)
  places one blue creature in the lower-left corner (`L41-45`, `L60-63`), makes
  all on-screen creatures look at the first animated mobject of every `play`
  (`L156-185`), and auto-blinks during `wait` every `seconds_to_blink = 3`
  seconds (`L39`, `L212-226`). `TeacherStudentsScene` (`L255-388`) sets a
  `GREY_E` background (`L258`), three students in `BLUE_D`, `BLUE_E`, `BLUE_C`
  at lower-left scaled 0.8 and a grey-brown teacher at lower-right (`L256-257`,
  `L283-298`), a 4-unit black screen in the upper-left (`L261`, `L266-271`), a
  `hold_up_spot` above the teacher (`L272`), and helpers `teacher_says`,
  `student_says` (random raised hand, `L309-329`), `change_students` with
  `lag_ratio = 0.5` (`L351-360`), and `teacher_holds_up` (`L380-388`).

Usage is heavy: 91 `TeacherStudentsScene` subclasses in 2025-2026 and 63 plus 12
`PiCreatureScene` subclasses in the neural-network and transformer series. A
typical use is a short reaction cut, for example `DiscussTrilogy`
(`_2025/laplace/supplements.py:L150-179`) which changes student moods with
`self.change_students("pondering", "erm", "sassy", look_at=...)` between waits of
2, 3 and 6 seconds (`L167`, `L173`, `L179`). The SVG mode files are not public
and the characters are brand assets; the skill cannot ship Pi creatures. What
transfers is the role they play: a reaction beat that voices a learner's
objection or confusion between explanatory beats.

### 2.7 Drawings, deprecated animations and filler

- `custom/drawings.py`: SVG-backed props (`Car` with rolling tires via
  `MoveCar`, `L5-127`; `PartyHat`, `SunGlasses`, `Headphones`, `Guitar`,
  `L130-207`), a procedural `PlayingCard`/`DeckOfCards` (`L212-449`), and two
  third-party logos (`L461-484`). All depend on named SVG files that are not in
  the repo.
- `custom/deprecated.py:L10-22`: `FadeInFromDown`, `FadeOutAndShiftDown`,
  `FadeInFromLarge`, kept so old scenes import; the header explains they are now
  arguments to `FadeIn`/`FadeOut` (`L1-5`).
- `custom/filler.py:L4-6`: `ExternallyAnimatedScene` raises on `construct`.
  It is a named placeholder for footage made outside Manim; the neural-network
  and transformer files subclass it 8 times (class-base census).

### 2.8 Legacy constructs (`once_useful_constructs/`)

Twenty-one modules of older scene bases and mobjects: `GraphScene`
(`graph_scene.py:L27`, with a header noting it should be replaced by `Axes`,
`L22-24`), `VectorScene` and `LinearTransformationScene`
(`vector_space_scene.py:L52`, `L283`), `ComplexTransformationScene`,
`CountingScene`, fractal and space-filling-curve mobjects (`fractals.py`),
light-cone mobjects (`light.py`), probability `SampleSpaceScene`, and
`digest_config` from the `CONFIG`-dict era (`dict_shenanigans.py:L13`, marked
deprecated). Only 9 import sites reference the package anywhere and none in
2024-2026, so these are not current conventions; `GraphScene` is still a base in
the 2017 neural-network files (4 subclasses).

## 3. The interactive development workflow

### 3.1 The loop as the README describes it

`README.md:L15-50` documents two primitives. Running
`manimgl <file> <Scene> -se <line>` drops into an IPython terminal at that line
"like a debugger" (`L21`). Inside it, `checkpoint_paste()` runs whatever code is
on the clipboard; if the pasted block starts with a comment, the first run saves
the scene state under that comment and every later run of a block with the same
leading comment first reverts to that state (`L23`). `skip=True` runs with zero
run time, `record=True` renders the block to file (`L24-25`). Sublime
keybindings drive these (`L36-43`): run scene, checkpoint paste, recorded
paste, skipped paste, exit. `CLAUDE.md:L11-19` repeats the commands and
`CLAUDE.md:L53-56` states the scene workflow: subclass `InteractiveScene`,
develop with `-se`, iterate with `checkpoint_paste()`, preview, then render.

### 3.2 Mechanics in ManimGL source

- `-s` is "skip animations" (`manimlib/config.py:L73-77`) and `-e LINE` inserts
  a breakpoint (`L164-169`); together `-se N` fast-forwards to line `N` and
  embeds. `insert_embed_line_to_module` rewrites the module source with
  `self.embed()` inserted at that line and infers the scene class from the
  nearest `class` above it (`manimlib/extract_scene.py:L146-178`). `embed()`
  returns immediately without a window, stops skipping, draws a frame and
  launches the shell (`manimlib/scene/scene.py:L203-219`).
- The shell namespace gets shortcuts: `play`, `wait`, `add`, `remove`, `clear`,
  `focus`, `save_state`, `undo`, `redo`, `i2g`, `i2m`, `checkpoint_paste`,
  `clear_checkpoints`, `reload` (`manimlib/scene/scene_embed.py:L61-82`). The
  window keeps redrawing while the shell waits for input (`L84-100`) and every
  cell ends with a forced frame update (`L102-108`); exceptions flash a red
  border (`L110-119`).
- `CheckpointManager.checkpoint_paste` reads the clipboard with `pyperclip`,
  dedents it, takes the first line as the key if it is a comment, restores the
  saved state for a known key and discards all later keys, or saves a new state
  for an unknown key, then runs the cell (`L208-245`).
- `skip` and `record` map onto context managers: `temp_skip` (`scene.py:
  L684-691`), `temp_record` which opens an insert file at output resolution
  (`L703-710`), combined by `temp_config_change` (`L711-719`). `save_state`,
  `undo`, `redo` keep up to 50 states (`L57`, `L664-682`).
- `reload(line)` validates syntax, sets `is_reload` and the new embed line, and
  raises out of IPython (`scene_embed.py:L146-184`); the main loop catches it
  and re-runs extraction with the same window (`manimlib/__main__.py:L20-46`).
  `embed.autoreload: True` (`custom_config.yml:L32`) re-imports the module
  before every cell (`scene_embed.py:L186-192`).
- `InteractiveScene` adds mouse selection, grabbing, resizing, a color palette,
  a cursor-coordinate label, and clipboard helpers `copy_frame_positioning` and
  `copy_cursor_position` (`manimlib/scene/interactive_scene.py:L61-80`, `L635`,
  `L650`). This is how exact coordinates and camera poses such as
  `frame.reorient(-52, -2, 0, (-1.74, -7.1, -0.03), 14.72)` end up in source
  (`_2024/transformers/attention.py:L1423`).
- `-p` is presenter mode, which pauses on every `wait` until a key is pressed
  (`config.py:L103-108`; `scene.py:L621-624`). `CLAUDE.md:L14` describes `-p`
  as "preview without rendering"; the code is authoritative.
- Final renders use `--prerun -w` (`manim_plugins.py:L225`): `--prerun` does a
  skipped pass to count frames for the progress bar (`config.py:L193-198`,
  `extract_scene.py:L63-79`), `-w` writes the movie (`L68-72`); `-o` or
  `--finder` imply `-w` (`L227`). `-n a,b` renders only animations `a` to `b`
  (`L157-163`).

### 3.3 The Sublime glue

`sublime_custom_commands/manim_plugins.py` turns editor state into terminal
commands via Terminus (`README.md:L31`):

| Command | Behavior | Lines |
| --- | --- | --- |
| `manim_run_scene` | Save; if the terminal is already in IPython send `reload(<cursor line>)`, else build `manim <file> <Scene> -se <line>` from the nearest `class` above the cursor | `L10-47`, `L158-182` |
| `manim_checkpoint_paste` | Save, copy the selection, send `checkpoint_paste() # <leading comment> (<n> lines)`; a single non-comment line is sent verbatim | `L130-155`, `L192-195` |
| `manim_recorded_checkpoint_paste` | Same with `record=True, progress_bar=False` | `L198-200` |
| `manim_skipped_checkpoint_paste` | Same with `skip=True` | `L203-205` |
| `manim_exit` | Send Ctrl-C and `quit` | `L185-189` |
| `manim_render` | Stage `manim <file> <Scene> --prerun -w` in a "Rendering" terminal without pressing enter | `L215-230` |
| `open_mirrored_directory` | Open the Dropbox output folder for the current file | `L233-245` |

### 3.4 What this does to the code

Because a checkpoint is keyed by a leading comment, each `construct` is written
as a sequence of comment-headed blocks, each a narrative beat that can be
re-run in isolation. The first block is frequently a placeholder `# Test`: 405
`construct` methods in 2024-2026 start with that exact line. Named beats look
like `# Add definition` (`_2025/laplace/supplements.py:L6`), `# Reference last
two` (`L159`), `# Moving sectors` (`L612`). The beat comment is the atomic unit
of iteration, and therefore the natural unit to align with a narration
sentence or paragraph.

### 3.5 An agent-driven equivalent in ManimCE

An agent has no window, clipboard or IPython session, so the loop must be
rebuilt from batch primitives. ManimCE already has the pieces:

| Human step in ManimGL | Headless ManimCE equivalent | Source |
| --- | --- | --- |
| `-se N` fast-forward to a beat | `self.next_section("beat")` per beat plus `--save_sections` to get one clip per beat; `-n a,b` to render an animation range | `manim/scene/scene.py:L378-388`; `manim/cli/render/render_options.py:L260-263`, `L138-141` |
| Look at the window | `-s` saves the last frame as PNG; extract mid-clip frames from section videos with ffmpeg | `render_options.py:L172-176` |
| `checkpoint_paste(skip=True)` | `--dry_run` renders without output to check logic and LaTeX | `manim/cli/render/global_options.py:L112-114` |
| Cheap iteration | `-ql` (854x480 at 15 fps) during authoring, `-qk --fps 30` for the final | `manim/constants.py:L206-236`; `render_options.py:L180-187`, `L206-211` |
| Unchanged beats are not re-run | Partial-movie caching keyed by animation hash | `manim/scene/scene_file_writer.py:L350-371`, `L691` |
| Reproducible randomness | `--seed` | `global_options.py:L129-131` |
| Reading coordinates off the GUI | Programmatic layout only (`arrange`, `next_to`, `to_edge`) and an assertion helper that checks bounding boxes stay inside the frame | `CLAUDE.md:L113-115` guidance |
| Record a snippet | Section videos written by `combine_to_section_videos`, indexed in JSON | `scene_file_writer.py:L966-984` |
| Carry the narration text along | `add_subcaption` writes an SRT beside the video | `manim/scene/scene.py:L1726-1766`; `scene_file_writer.py:L986-994` |

`interactive_embed` and `embed` exist in ManimCE (`manim/scene/scene.py:L1439`,
`L1602`) but need a window and a human; they are out of scope for the agent.
The skill's preview loop should therefore be: render one section at `-ql`,
inspect the last frame and one or two mid-beat frames, check bounding boxes,
fix, re-render only that section, and only at the end render everything at
`-qk --fps 30`.

## 4. How a video is assembled from scenes

### 4.1 Units of production

A scene class is a clip. Each `manimgl <file> <Scene> -w` run produces one
`<Scene>.mp4` in the mirrored Dropbox folder (section 1.4). Within a project
folder, files split by chapter or topic (`_2025/laplace/{shm,exponentials,
integration,derivatives,main_equations,prequel_equations}.py`) and each has a
companion `*supplements.py` for short overlays and reaction cuts
(`_2025/laplace/supplements.py`, `derivative_supplements.py`,
`main_supplements.py`; `_2026/cross_entropy/supplements.py`,
`part2_supplements.py`). `CLAUDE.md:L38-43` names this layout.

### 4.2 Ordering and staging

`stage_scenes.py` is the only in-repo assembly tool. It orders scenes by an
explicit `SCENES_IN_ORDER` list if the module defines one, else by definition
order via `inspect.getsourcelines` (`L11-31`), collects every rendered file whose
name starts with `<Scene>.` (`L47-51`), and creates a fresh `staged_scenes_N`
directory of symlinks named `Scene_<count:03>_<file>` in reverse order so a
date-sorted Finder window shows them in sequence (`L66-89`). It is stale: the
animation directory is hard-coded to a 2021 project behind a `TODO` (`L39-43`)
and it calls `get_module(module_name)` (`L12`) although the current
`extract_scene.get_module` takes a config object (`manimlib/extract_scene.py:
L181-185`). `CLAUDE.md:L22` still lists the command.

`SCENES_IN_ORDER` appears only in 2019-2020 work: `_2019/diffyq/
all_part1_scenes.py:L1-8` star-imports five part modules and lists the
sequence with an `OUTPUT_DIRECTORY`, and `_2020/sir.py:L3310-3340` keeps a
`WILL_BE_SCENES_IN_ORDER` headed "For assembling script" with narrative
section comments such as `# Quarantining`, `# Social distancing`, `# Describing
R0`, `# Market`. Placeholder scenes mark footage made elsewhere:
`ShowCubeDVIn3D` raises "only here for the stage_scenes script"
(`_2017/eoc/chapter3.py:L1193-1195`); `TODOStub` (`_2018/fourier.py:L60`) is
subclassed 9 times and `ExternallyAnimatedScene` 8 times in the neural-network
and transformer files.

Recent projects rely on definition order plus chapter-marker comments instead:
`# Intro chapter` and `# Attention chapter` (`_2024/transformers/supplements.py:
L6`, `L838`), `# For chapter 5/6/7` (`_2024/transformers/embedding.py:L116`,
`L2230`, `L2569`). `CLAUDE.md:L60-61` asks for chronological order and class
names that match the video content. Suffix conventions in 2024-2026: 10 classes
end in `Ambient...` (looping background shots), 6 in `Thumbnail`, 6 in `Test`.

The final cut is made outside Manim. The repo contains no editing or
concatenation code beyond `stage_scenes.py`; per-scene MP4s, `inserts/` clips,
Finder-oriented staging and black `VideoWrapper` placeholders all presuppose a
video editor. Which editor is unverified.

### 4.3 Implications for aligning transcript sections to scene classes

- Scene class names are descriptive and chronological (`IntroduceTrilogy`,
  `DiscussTrilogy`, `WhoCares`, `_2025/laplace/supplements.py:L4`, `L150`,
  `L182`), so for corpus analysis the key `(file, definition index, class name,
  beat comments)` is the right join key against transcript paragraphs. Expect
  many-to-one: a transcript paragraph often spans a main scene plus one
  `TeacherStudentsScene` reaction from `supplements.py`.
- Overlays are a second track. The transcript never marks them, and the
  alignment schema needs a `kind` field (`main`, `overlay`, `ambient`,
  `thumbnail`, `end_screen`) so the analyzer can ignore non-teaching scenes.
- For generation the skill should not inherit the two-track layout. One run
  must yield one MP4, so the plan should be a manifest `sections[] = {id, title,
  narration, scene_class, beats[]}`, one `Scene` per section in a single file in
  manifest order, `self.next_section(beat_id)` per beat, `--save_sections` on,
  and a final ffmpeg concat in manifest order. ManimCE's section JSON index
  (`scene_file_writer.py:L979-984`) then doubles as the timing record for
  narration alignment.
- Keep the `SCENES_IN_ORDER` idea as an explicit list in the generated module;
  it is cheap, it survives refactors, and `stage_scenes.py:L13-14` shows it was
  the intended contract.

## 5. Conventions

### 5.1 Imports and paths

- `from manim_imports_ext import *` is the first line of every scene file
  (`CLAUDE.md:L59`; 370 files). Scenes are run from the repo root so that
  absolute package imports resolve: `from _2025.laplace.exponentials import
  SPlane` (`_2025/laplace/main_equations.py:L2-4`), `from
  _2024.transformers.helpers import *` (`_2024/transformers/attention.py:L4`).
  Cross-project reuse happens the same way (`from _2024.transformers.helpers
  import Dial`, `_2026/cross_entropy/supplements.py:L7`).
- The README's alternative is three `sys.path.append` lines at the top of a
  file (`README.md:L77-79`); the 2017 files do a one-level variant
  (`_2017/nn/part1.py:L1-5`) and import their helper package as `from
  nn.network import *` (`L17`).
- Folder renames leave stale imports: `_2025/grover/state_vectors.py:L2`
  imports `_2025.blocks_and_grover.qc_supplements`, a path that no longer
  exists. `README.md:L6` warns that older projects may not run as-is.
- `_2017/nn/part1.py:L9-14` warns that it relies on the deprecated
  `ContinualAnimation`, and `L19-20` carry `#force_skipping` and
  `#revert_to_original_skipping_status` comments, the 2017 ancestors of
  `checkpoint_paste(skip=True)` (methods still exist at `manimlib/scene/
  scene.py:L633-641`).

### 5.2 File layout per project

`_YYYY/<project>/` holds: main scene files named by topic or part
(`part2.py`, `planets.py`, `entropy.py`), `supplements.py` for overlays, a
`helpers.py` or topic module for shared mobjects and functions
(`_2024/transformers/helpers.py`; `_2026/cross_entropy/{distribution,
next_char}.py`), data files beside the code (`_2026/cross_entropy/
huffman_table.json`, `text_data/`), vector art sources (`_2026/cross_entropy/
images/*.ai`), and standalone experiments that do not import Manim at all
(`_2024/transformers/almost_orthogonal.py`). Scene files run 600 to 8800
lines; `_2026/cross_entropy/robot.py` is 8801 lines.

### 5.3 Scene base classes

Census of direct base classes (regex over `^class Name(Base):`):

| Base | 2025-2026 | 2017 nn + 2024 transformers |
| --- | --- | --- |
| `InteractiveScene` | 634 | 123 |
| `TeacherStudentsScene` | 91 | 63 |
| `Scene` | 2 | 39 |
| `PiCreatureScene` | 0 | 12 |
| `SideScrollEndScreen` / `PatreonEndScreen` | 10 / 7 | 0 / 2 |
| `ExternallyAnimatedScene` / `TODOStub` | 0 | 8 / 9 |
| `GraphScene` | 0 | 4 |
| project-specific bases (for example `SPlane`, `BasicBlockCount`) | dozens | dozens (`SimpleAutogregression` 27) |

`InteractiveScene` is the universal base today (`CLAUDE.md:L72`). Scene-level
configuration is done with plain class attributes overridden in subclasses, for
example `initial_velocities`, `masses`, `clack_sound`, `field_of_view`
(`_2025/colliding_blocks_v2/blocks.py:L95-106`) and `dimensions`
(`_2026/cross_entropy/supplements.py:L10-35`, five `SimpleRect` variants that
differ only by one attribute). `setup()` is used for shared construction before
`construct()` (`blocks.py:L108-115`; `manimlib/scene/scene.py:L167-173`).
Variant scenes subclass a finished scene and override one attribute or method
(`SingleNullPointHairyBallRevealed(SingleNullPointHairyBall)`,
`_2026/hairy_ball/spheres.py:L852`).

In ManimCE the mapping is `Scene` or `MovingCameraScene` for 2D,
`ThreeDScene` for 3D, no interactive base; class-attribute configuration ports
unchanged.

### 5.4 Helper placement

Reusable mobjects and functions live in a project `helpers.py`
(`_2024/transformers/helpers.py`: `DATA_DIR` at `L9`, functions `L18-340`,
mobject classes `NeuralNetwork`, `WeightMatrix`, `EmbeddingArray`, `Dial`,
`MachineWithDials` at `L342-761`) or at the top of the scene file above the
first scene (`_2026/cross_entropy/entropy.py:L11-89` defines `bit_string_
mobject`, `InstructionArrow`, `ProbIcon` before the first `InteractiveScene`).
Scene methods that build parts use a `get_*` prefix (`CLAUDE.md:L97`;
`get_pi_frac_texs` in `_2025/laplace/main_equations.py:L38`). Repo-wide
components go in `custom/`.

### 5.5 Coding idioms stated in `CLAUDE.md` and confirmed in recent code

- `Tex(R"...")` with raw strings and `t2c` color maps (`CLAUDE.md:L82-83`,
  `L101`); 1548 `Tex(` and 363 `t2c=` occurrences in 2025-2026, zero `OldTex`.
  `Text(` has 731 uses, `TexText(` 168.
- `lag_ratio` staggering and `LaggedStart` (`CLAUDE.md:L84`, `L108`).
- `play` then `wait`: 4772 `self.play(` and 3012 `self.wait(` in 2025-2026,
  roughly two plays per three waits, with explicit wait lengths tuned per beat.
- Updaters via `add_updater` or `f_always` (`CLAUDE.md:L106-107`).
- Declarative `VGroup(... for ...)`, `color_gradient`, layout by `arrange`,
  `next_to`, `move_to` instead of coordinate arithmetic (`CLAUDE.md:L113-115`).
- Blank lines contain no whitespace (`CLAUDE.md:L111-112`).
- Testing is visual only: "No formal testing framework - scenes are tested
  through visual preview and rendering" (`CLAUDE.md:L123`).

### 5.6 Infrastructure-level ManimGL to ManimCE translation

| ManimGL (as used in the repo) | ManimCE |
| --- | --- |
| `from manim_imports_ext import *` | `from manim import *` plus the skill's own `patterns` module |
| `InteractiveScene`, `self.frame`, `frame.reorient` | `MovingCameraScene` with `self.camera.frame`, or `ThreeDScene` with `set_camera_orientation` / `move_camera` |
| `mob.fix_in_frame()` | `self.add_fixed_in_frame_mobjects(mob)` in `ThreeDScene`; keep HUD static in 2D scenes |
| `Tex` (math), `TexText` (text mode) | `MathTex`, `Tex` (`CLAUDE.md:L82` warns the names differ) |
| `Text(font="CMU Serif")` by config | `Text.set_default(font=...)` or per-call `font=` (font availability on the render host is unverified) |
| `custom_config.yml` | `manim.cfg` beside the scene file (`manim/_config/utils.py:L85`) |
| `-w`, `--uhd`, `--fps 30` | `-qk --fps 30` or `-r 3840,2160 --fps 30` |
| `-s` (skip, save last frame) | `-s` (`render_options.py:L172-176`) |
| `-n a,b` | `-n a,b` (`render_options.py:L138-141`) |
| `--subdivide`, `inserts/` | `--save_sections` with `next_section` |
| `add_sound` muxed as AAC at finish | `add_sound` exists (`manim/scene/scene.py:L1768`); for narration prefer an external ffmpeg mux after concat |
| `saturation: 1.5` file-writer option | apply `-vf eq=saturation=1.5` in the final ffmpeg pass if the look is wanted |

## 6. Narration and animation coordination

Neither `README.md` nor `CLAUDE.md` mentions audio, scripts, narration or
voice-over. The code gives only indirect evidence:

- Narration is recorded and placed outside Manim. `add_sound` is used only for
  simulation sound effects (`_2025/colliding_blocks_v2/blocks.py:L100-101`,
  `L1109`; `_2023/clt/galton_board.py:L386`; `_2019/hyperdarts.py:L186`), never
  for speech. The repo has no transcript, script or audio files.
- Animation is written to fit narration, not the reverse. Comments say so
  directly in older work: "Repeat for effect, goes well with narration"
  (`_2018/WindingNumber.py:L2062`), "Images matched to narration's introductory
  list" (`_2018/alt_calc.py:L597`), a `SCENES_IN_ORDER` list headed "For
  assembling script" (`_2020/sir.py:L3310`). In recent code the fit is encoded
  as hand-tuned `wait` durations between beats (`self.wait(2)`, `self.wait(3)`,
  `self.wait(6)` in `_2025/laplace/supplements.py:L167`, `L173`, `L179`) and in
  long ambient holds meant to be trimmed in the edit (`VideoWrapper.wait_time =
  32`, `custom/backdrops.py:L41`; "Set longer to interact with in a recording",
  `_2026/print_gallery/exponential.py:L2618`).
- Presenter mode (`-p`, `manimlib/config.py:L103-108`) holds each `wait` until a
  key press, which supports stepping an animation while speaking, and
  `checkpoint_paste(record=True)` writes isolated beat clips to `inserts/`
  (`manimlib/scene/scene_file_writer.py:L258-278`). Whether he narrates first
  and animates to the audio, or animates first and records to picture, is
  unverified; the editor-centric evidence above suggests the timing is resolved
  in the edit.

Implication for the skill: because there is no editor in the loop, timing must
be resolved in code. The design that matches the evidence is narration-first per
section: synthesize each section's audio, measure its duration, give the section
scene a duration budget, let beats consume their natural `run_time`, and pad
with `self.wait(remaining)` at beat boundaries; carry the narration text into
`add_subcaption` so the SRT doubles as an alignment check. The per-beat
`next_section` boundaries and the JSON index give the timestamps needed to
verify that each sentence lands on its visual.

## 7. Gaps, risks and unverified items

- Rendered documentation for ManimGL and ManimCE was unreachable; all behavior
  above is from library source at the commits named in the sources section.
  `docs.manim.community` should be re-checked for `--save_sections`, `-n` with
  `-s`, and quality presets when the network is open.
- The YouTube workflow video linked from `README.md:L17` was not watched.
- Whether `-s` combined with `-n a,b` in ManimCE saves the frame at the end of
  animation `b` is unverified; it determines how mid-scene stills are taken.
- Whether `Banner.camera_config` (`custom/banner.py:L20`) still takes effect is
  unverified; the attribute name does not match `Scene.default_camera_config`.
- CMU Serif availability on a Linux render host, and the exact TeX Live package
  set needed for the ported preamble, are unverified.
- The video editor and the narration-recording order are unverified; the
  conclusions in section 6 are inferences from code.
- Pi creature SVGs, raster assets, sound files and patron data are not in the
  public repo (zero image files found); any scene that depends on them cannot be
  re-rendered for keyframe checks.
- `stage_scenes.py` is stale against current ManimGL (`L12` versus
  `manimlib/extract_scene.py:L181-185`) and hard-codes a 2021 path (`L39-43`).
- `CLAUDE.md:L14` and `manimlib/config.py:L103-108` disagree on what `-p` does;
  this map follows the code.
- The "Ultracode" method named in the triggering request is not available in
  this kit: `/home/user/.agents/CHANGELOG.md:L57-58` records that the
  `ultracode` skill was removed, and no skill by that name is loaded. This map
  was produced with the kit's standard look-it-up and minimal-change rules.

## 8. Key implications for the skill design

1. Target 3840x2160 at 30 fps on a pure black background for final renders
   (`custom_config.yml:L20-23`); iterate at `-ql` and finish with `-qk --fps 30`.
2. Ship a `TexTemplate` that extends ManimCE's three-package default with the
   packages the 3b1b preamble relies on (`manimlib/tex_templates.yml:L3-28`
   versus `manim/utils/tex.py:L21-23`) and document the TeX Live dependency.
3. Treat the comment-headed beat as the unit of authoring and alignment; map it
   to `next_section(beat_id)` with `--save_sections`, and use the section JSON
   index as the timing record.
4. Replace the GUI loop with a batch loop: dry run, low-quality section render,
   last-frame and mid-beat stills, bounding-box checks, re-render only the
   changed section.
5. Generate one scene per transcript section in one module with an explicit
   ordered list, then concatenate with ffmpeg and mux narration externally;
   do not reproduce the two-track main-plus-supplements layout.
6. Resolve timing in code, narration-first, with per-section duration budgets
   and `wait` padding at beat boundaries; emit SRT via `add_subcaption` for QA.
7. Pi creatures, the logo, end screens and banners are brand assets whose SVGs
   are not public; the skill needs an original device for the "learner
   objection" beat or must drop it.
8. Keep the house layout idioms (`arrange`, `next_to`, `to_edge`, class-attribute
   configuration, `get_*` builders, `t2c` color maps) and port camera work to
   `MovingCameraScene` and `ThreeDScene`.
9. Record the ManimGL to ManimCE renames (`Tex`/`TexText` to `MathTex`/`Tex`,
   `fix_in_frame` to `add_fixed_in_frame_mobjects`, `reorient` to
   `set_camera_orientation`) in the pattern library so translated examples do
   not import ManimGL-only names.
