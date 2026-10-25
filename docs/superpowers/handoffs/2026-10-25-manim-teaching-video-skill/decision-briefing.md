# Decision briefing for the nine owner decisions

Background the owner asked for before deciding the nine items in
`design-proposal.md`. Numbers come from the evidence maps (cited as map NN and
section) or from checks run in the design session; anything not measured is
marked as an estimate.

## 1. Where the corpus tooling lives

What the tooling is: about nine Python scripts (fetch captions and figures,
transcribe, split source into scenes, align transcript sections to scenes,
narration statistics, citation checker, census, sync to kit), each a few
hundred lines. Estimate: well under one megabyte of text in total. The tools
themselves never bloat anything.

What would bloat a repository is the data the tools produce, if it were
committed (map 07 section 5):

| Data | Size |
| --- | --- |
| Captions, timed (VTT or json3), all eight videos | 0.5 to 1 MB |
| Whisper word-level JSON, if used | 2 to 4 MB |
| Lesson figures from the site's public bucket, jpg only | 100 to 130 MB |
| Scene-change keyframes, downscaled to 480p JPEG | 50 to 90 MB |
| Scene-change keyframes at 1080p JPEG | 0.3 to 0.6 GB |
| Downloaded 1080p videos (eight) | 1.7 to 4.5 GB (bitrate unverified) |
| Analysis records (our own words, JSON or Markdown) | about 1 MB for all eight |

Every design keeps the data out of git in a gitignored cache and commits only
the analysis records, the framework, the pattern library and the rubric. So
the location question is about megabytes of scripts, not gigabytes.

Are the tools kit-wide or skill-specific? Skill-specific, and build-time only.
They run once per corpus revision to produce the skill's reference files; the
skill never calls them while making a video, and no other skill uses them.
The three placements differ in what else they touch:

- Separate repository `manim-3b1b-corpus` (recommended): nothing in the kit
  changes; the kit's hygiene gates (typos, lychee, jscpd, shellcheck) never
  scan the tools; the third-party cache and the CC BY-NC-SA analyses have a
  natural home under their own license. Cost: a second repository to clone
  when the corpus is revised.
- `tools/corpus/` at the kit root: not installed to consumers (the installer
  maps only `skills/`, `agents/`, `rules/` and `agents.kit.md`), but scanned
  by every hygiene gate, so every script and fixture must pass typos, jscpd
  and the rest, and the kit's README must explain a directory that has
  nothing to do with using the kit.
- Inside `skills/manim-teaching-video/tools/`: after the installer change
  every consumer who installs the kit receives build-time tooling they will
  never run, plus its requirements file.

## 2. Storing the release media

The key design fact: the skill does not consume the media or the corpus at
run time. The load-order table in the proposal (section 7) has the parent
agent load only the header and gate results; the scriptwriter reads the
framework rules; the storyboarder adds the pattern index; a scene coder reads
its scene, the docstrings of the helpers it names and the ManimCE table;
critics read the rubric. Nothing reads a transcript, a keyframe or a video.
The media is consumed once, at build time, by the analysts who write the
analysis records, and the rules those records support are what the skill
ships. That is also what the license requires (map 06 section 6; map 07
section 6): frames from his videos and his transcripts cannot ship in an MIT
kit at all.

So the storage question is about the private build-time cache, and the
answer is a per-video folder, never committed:

- `captions/`: the YouTube caption file as fetched (json3 keeps word-level
  timing; about 100 KB per video).
- `figures/`: the lesson's figures from the site's public bucket, jpg only
  (about 15 MB per lesson). These are already captioned stills chosen by the
  author, which is why the proposal prefers them to extracted keyframes.
- `keyframes/`: optional, only if videos are downloaded. One JPEG per scene
  change, downscaled to 854 by 480 (about 40 KB each, 150 to 300 per video),
  plus one `keyframes.json` listing timestamps and the nearest caption
  words. Optionally one six-frame contact sheet per transcript section, which
  is the form an analyst can read in one image. The full video is deleted
  after extraction; re-extraction is one `ffmpeg` command from a fresh
  download, so there is nothing to keep.
- `analyses/`: our records, which are committed (to the corpus repository
  under option A of decision 8).

There is no fancier compressed format worth building: JPEG at 480p already
puts a whole video's keyframes in 10 to 20 MB, the captions are text, and
the only thing the skill needs downstream is the words the analysts write.

Decision 2 therefore asks only: at release, do we fetch captions and the
bucket figures (recommended, no YouTube download, no terms-of-service
exposure), or also download the eight videos to extract keyframes? The maps
estimate 1,100 to 2,200 keyframes across the series. Keyframes add evidence
for motion and timing that stills cannot show; the code gives the same
information exactly (run times, waits, animation classes), which is why the
proposal treats keyframes as a secondary check. Downloading is a
terms-of-service risk even for private study (map 07 section 6, wording
third-party). The recommendation is to start without it and add it in the
extension loop if the analysts report that code plus figures leave motion
questions open.

## 3. Inlined role prompts versus entries under `agents/`

The five roles are scriptwriter, storyboarder, storyboard critic, scene coder
and frame critic. The two forms look like this.

Inlined, in `references/roles.md`, one block per role, read by the parent
when it dispatches a generic subagent:

```text
## Scene coder

Goal: write one ManimCE Scene subclass for scene <id> of lesson.json.
Inputs: the scene object (beats, marks_s, visual, patterns), the docstrings
  of the helpers it names, references/manimce.md.
Rules: import helpers from mtv.patterns; never recall ManimGL idioms;
  cite the rule id you applied in a comment at the top of each beat.
Output: lesson.py fragment; a list of rule ids applied.
```

As kit agents, five files `agents/mv-<role>/agent.md` with the kit's agent
frontmatter contract and a body in the same voice as the review agents:

```yaml
---
connection-type: internal
description: Use as part of the manim-teaching-video pipeline. Receives one scene of lesson.json and writes its ManimCE Scene subclass using the shipped pattern helpers.
enabled: true
id: mv-scene-coder
name: Scene Coder
role: delegation-target
---
```

What differs in practice:

- Where they run. The kit's `agents/` folder is read by .agents Protocol
  consumers such as OpenCode, where each entry becomes a selectable agent
  that the consumer can map to a model tier in `models.json`. Claude Code
  reads its own `~/.claude/agents/` directory for subagent definitions, not
  `~/.agents/agents/`, which is why every kit skill already carries the
  fallback "if a named type is unavailable, use the harness's generic agent
  with that definition inlined" (map 06 section 4.1). In Claude Code the
  inlined form is what runs either way.
- Kit bookkeeping. Agents need five new directories, a roster row in the
  README's sub-agents table, and an extension of the validator's agent-name
  pattern (it currently recognizes only `cr-*` and `research*` names, so
  `mv-*` references in a skill would otherwise not be checked). Inlined
  prompts are one reference file and nothing else.
- Reuse and visibility. An agent entry can be invoked directly by the owner
  or by a future skill (a frame critic is plausibly reusable); an inlined
  prompt is private to this skill.
- Change cost. Editing a role is one edit either way; promoting an inlined
  role to an agent later is a copy plus the bookkeeping above, which the
  proposal schedules for the extension loop "when a second skill reuses
  them".

Recommendation stands: inline for v1, promote on reuse.

## 4. What a hard LaTeX requirement entails

ManimCE does not typeset math itself and there is no Python LaTeX package
involved. When a scene creates `MathTex` or `Tex`, Manim writes a `.tex`
file, runs the system `latex` binary to produce a DVI, then runs `dvisvgm`
to turn it into SVG paths it can draw (map 04, "Text, MarkupText, Tex,
MathTex, Typst and the LaTeX requirement"). The requirement is therefore a
system install of a TeX distribution on whatever machine renders the video,
not a dependency of the kit or of the skill's Python requirements.

What breaks without it: every `Tex` and `MathTex`, and everything built on
them, which in ManimCE includes `DecimalNumber`, `Integer` and `Variable`
(digits are rendered as `MathTex` by default), `Matrix`, axis numbers,
`Brace` labels and vector coordinate labels (map 04, same section). For a
math teaching video that is most of the number-bearing visuals.

Install cost: ManimCE's default preamble is 3b1b's, and it loads packages
that on Debian-family systems live in `texlive-fonts-extra` and
`texlive-science` on top of the base LaTeX packages. The proposal calls
this a multi-gigabyte install and has M0 measure it. A minimal TeX Live
with only the base and recommended packages is several hundred megabytes,
but then some preamble packages are missing and must be dropped from the
template.

Alternatives, and why the proposal does not recommend them for v1:

- Typst: `pip install "manim[typst]"` bundles a compiler, so no TeX
  distribution is needed, and `Typst` and `MathTypst` render formulas (map
  04). But the number-bearing classes above still default to `MathTex`, so
  every pattern helper that shows a changing number or a matrix would need
  a Typst or `Text` twin, and `DecimalNumber(mob_class=Text)` is only
  plausibly supported (map 04 marks it unverified). Two math engines double
  the pattern library and the tests.
- Text only: Pango `Text` and `MarkupText` need no LaTeX and are always
  available, but they cannot typeset real math layout (fractions, sums,
  matrices), which is exactly what the corpus is full of.

So "hard requirement" means: the skill's preflight checks for `latex` and
`dvisvgm` and stops with the install command when they are absent, and the
owner installs TeX Live once per rendering machine. For the cloud
environment that means a setup script line (see the README checklist).

## 5. Corpus depth at release

Plain statement of the decision: how many of the eight videos receive the
full, cited, per-section analysis before the skill ships.

The seven maps already read every line of the series code, so the
framework's rules, colors, timings and moves are grounded in all eight
videos at the level of "what the code does" (map 01 sections 3 to 8; map 02
sections 3 to 8). The per-section analysis adds the layer the code cannot
give: what the narration says while each visual plays, the order of ideas,
where questions are planted, how long each idea gets, and a cited record
per transcript section that a rule can point at. Each video needs about 30
minutes of alignment by a reader, then one analyst per transcript section
(roughly 20 to 40 per video), a merger and a refuter, in waves of four to
six subagents (proposal section 5).

Two videos (recommended): chapter 1 of 2017 (2D, one source file) and the
2024 attention chapter (3D camera, role colors, multi-file). Both visual
regimes are covered, the citation checker and census are proven on one easy
and one hard case, and the first video ships about a week sooner. The other
six run through the identical pipeline afterwards, and each adds citations
and possibly rules; the proposal calls this the extension loop.

All eight first: the framework's citations are complete at release and no
rule rests on two videos' evidence alone. Cost: roughly four times the
analysis effort before anyone sees the first rendered video, and the risk
that a flaw in the analysis method is discovered after eight videos
instead of two.

## 6. Render times

Not yet measured. No render ran in the design session, and the attempt in
this session failed before rendering: on Linux the `manimpango` dependency
has no prebuilt wheel and compiles against the Pango development headers,
which the container lacks, and the Debian package mirror is unreachable from
it. The implementation environment needs those system packages in its setup
script (README checklist), and M0 then measures real numbers on four CPUs.

What the design already fixes so that the decision can wait for numbers:

- The tiers are `draft` 854 by 480 at 15 fps, `standard` 1920 by 1080 at
  30 fps, `final` 3840 by 2160 at 30 fps. A `draft` frame has about one
  sixteenth of the pixels of a `standard` frame at half the frame rate, so
  the iteration loop costs a small fraction of a standard render, and the
  fix loop re-renders only failed scenes.
- ManimCE's Cairo renderer is single-threaded per scene, so the pipeline
  runs one process per scene, three at a time on four CPUs.
- The final render runs in the background with an estimate printed first,
  scaled from the draft pass by pixels and frames.

Expectation, not a measurement: Cairo rendering at 1080p30 of scenes of this
kind runs on the order of real time to a few times real time per core on
current CPUs, and each unique formula adds a LaTeX compile of well under a
second that is cached across renders. On that basis a five-minute standard
video would take roughly five to twenty minutes of wall clock with three
scenes in flight, and a 2160p final about four times longer. Decision 6 only
asks whether the 4K tier is built and tested in v1; it is a configuration
file and a smoke test, cheap to add later, so the recommendation is to cap
v1 at `standard` and revisit with M0's numbers.

## 7. Reopening ADR-0002 for the bundled scripts

ADR-0002 says the kit carries no language rules: no per-language lint,
type-check, test or coverage gates in the kit's CI, because that
enforcement lives in the owner's `full-lint` reference repository and is
applied per project. The kit's CI runs only repo-wide hygiene (markdown
lint, spelling, links, secrets, duplicate code, shell lint) plus the kit
validator and an install smoke test.

The new skill ships about nine Python scripts and a small package, and the
proposal gives them a self-test, `selftest.py`, that runs without ManimCE.
Decision 7 asks whether the kit's CI should run that self-test on every
push (a Python step, which the ADR's wording excludes) or whether the
implementation session runs it manually before each commit and records the
output in the pull request (the recommendation, consistent with the ADR,
with the risk that a later edit to the scripts breaks them unnoticed until
someone runs a video).

A middle path, if the owner wants CI coverage: the ADR to be written for
this skill (ADR-0008, "skills may ship scripts and references") can state
that a shipped script's own self-test is a content check, not a language
rule, and add one CI line that invokes it. That keeps ADR-0002 intact in
spirit while covering the scripts. The recommendation is to decide this at
M4 when the scripts exist and their run time in CI is known.

## 8. License granularity of the analyses

The terms involved (map 06 section 6; map 07 section 6):

- `3b1b/videos` code is CC BY-NC-SA 4.0: attribution required, no
  commercial use, and any adaptation must carry the same license.
- The videos, their narration and the site's articles and figures are
  separately copyrighted; the site states all rights reserved with personal
  non-commercial evaluation permitted. YouTube's terms forbid downloading
  except as the service allows.
- This kit is MIT, and MIT cannot carry NonCommercial or ShareAlike terms.

Principles learned from studying a work, stated in our own words with a
citation (video, timestamp, file and line), are facts and ideas, which
copyright does not protect, so the framework, rubric and original pattern
code can ship under MIT with an attribution note. The question is the
analysis records: one per transcript section, each with a 40-to-120-word
paraphrase of the narration and a beat-by-beat description of what is on
screen. Summed over a 20-minute video that is a detailed abridgment of the
whole work, which is much closer to an adaptation than a principle is, and
an adaptation of CC BY-NC-SA material cannot be relicensed as MIT, nor used
commercially.

Option A (recommended): the analysis records stay in the corpus repository
under CC BY-NC-SA 4.0 (or private), and the kit ships only `framework.md`,
`patterns.md` and `rubric.md`, whose rules cite video id, timestamp, file
and line. The skill loses nothing, because the load-order table never reads
the analyses at run time. Option B: ship the analyses inside the skill with
an ADR arguing that factual descriptions of staging are not an adaptation.
That is a legal judgment this project cannot make for the owner; the
proposal's position is A until counsel or the owner says otherwise. Under
either option every shipped reference derived from the corpus carries an
attribution note naming 3Blue1Brown and both repositories.

## 9. Description style

The skill's frontmatter `description` is the text an agent reads to decide
whether to load the skill. Two conventions are in play.

The superpowers writing-skills rule: the description states only when to
use the skill, never what it does or how, because an agent that sees a
workflow summary may follow the summary instead of reading the skill body.
In that style:

```yaml
description: Use when the user wants a narrated teaching or explainer video with animated visualizations, mentions Manim or 3Blue1Brown-style animation, or asks to turn a topic or script into an animated lesson video.
```

The kit's own style, as in the `research` skill: a third-person statement
of what the skill does, followed by the trigger phrases:

```yaml
description: Produces a finished narrated teaching video from a topic (script, synthesized voice, ManimCE animation synced to the narration, rendered MP4). Use when the user asks for a Manim video, an animated explainer, a 3Blue1Brown-style lesson, or to turn a script into an animated teaching video.
```

The proposal follows the kit's style while honoring the part of the rule
that has evidence behind it: it never lists pipeline steps in the
description (map 06 section 5.1). Decision 9 asks the owner to confirm that
choice, or to switch the kit's house style to triggers-only for this skill.
The recommendation is the kit's style, for consistency with the two
existing skills.
