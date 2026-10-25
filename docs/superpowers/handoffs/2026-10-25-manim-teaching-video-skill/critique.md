# Critique of the manim-teaching-video design proposal

Verdict: not approvable as written, but close. No blocker, 10 major gaps, 22
minor gaps. The architectural choice (Approach C's spine and milestone order,
Approach B's run-time engineering, Approach A's evidence discipline) is
supported by the maps and by all three judgments, and most load-bearing
facts the proposal states were re-verified here against the ManimCE clone,
the PyPI records and the architecture files. The major gaps are
specification holes rather than wrong architecture: the sync contract has no
owner for marks and a gate that cannot fail, the scene base class cannot
serve 2D and 3D as written, the packaging has a `.gitignore` entry that
hides the shipped runtime, there is no asset or font policy, the eval plan is
unbudgeted, the research files it commits fail a CI gate today, and the
license position of beat-by-beat analyses needs an owner decision. Each is a
paragraph or a decision away from fixed; none requires reopening a settled
decision.

## Method and evidence

Read in full: `design-proposal.md` (668 lines), maps 01 to 07, the ranking
and "what none of them handles" sections of the three judgments, and the
shipping judgment's fact table. Spot-checked the three architecture files for
every number the proposal attributes to them.

Executed in this container:

1. `grep` and `sed` over the ManimCE 0.22.0 clone at
   `/home/user/ManimCommunity/manim` for every CE claim the proposal presents
   as fact (results in "Claims verified" below).
2. `git check-ignore` in a scratch repository to test the proposed
   `.gitignore` entry `mtv/` against the shipped package path.
3. `typos` 1.51.1 with the kit's `.typos.toml` over the whole `design/`
   directory and over the proposal alone.
4. `markdownlint-cli2` 0.18.1 (markdownlint 0.38.0, the only copy cached
   here; CI pins 0.23.2 with markdownlint 0.41.1, so MD060 could not be
   exercised) with the kit's `.markdownlint-cli2.jsonc` over all fourteen
   design files.
5. `typos` on a probe file containing the misspelled upstream identifiers
   quoted by maps 01 and 02.
6. PyPI JSON cached under the scratchpad for `manim`, `kokoro`, `elevenlabs`,
   `soundfile`, `manim-voiceover`.
7. Interpreter inventory (`python3.11`, `python3.12`, `python3.13`, `uv`,
   `apt-get` all present) for the M0 feasibility note.

Letters in the "Check" column refer to the brief's checklist: (a) undefined
components, (b) facts versus maps, (c) internal contradictions, (d) scope,
(e) kit rules, (f) feasibility, (g) licensing, (h) testability,
(i) ambiguity.

## Gap summary

| Id | Severity | Check | Gap in one line |
| --- | --- | --- | --- |
| G01 | major | a, c | Nobody owns the `<mark>` tags; the single-writer rule makes the storyboarder's `lands` field reference marks it cannot create |
| G02 | major | c, h | The 0.25 s sync gate compares offsets computed from the section index against audio placed at those same offsets; the proposal names this circularity as a defect of Approach C, then adopts it unchanged |
| G03 | major | a | `NarratedScene` has no stated base; CE `MovingCameraScene` and `ThreeDScene` are sibling classes, and the helpers `zoom_to` and `orbit_with_hud` need one each |
| G04 | major | a, e | No import path for `mtv` from the generated `lesson.py`, and the proposed `.gitignore` entry `mtv/` ignores `skills/manim-teaching-video/scripts/mtv/` (verified) |
| G05 | major | a, d | No asset, data or font policy; the proposal's own example beat needs "a digit image" that nothing in the design can produce |
| G06 | major | f, h | The eval pass rule needs 24 full-tier pipeline runs per iteration with render throughput unmeasured; no budget, no parallel plan |
| G07 | major | e | The maps the proposal commits to `docs/research/` fail the kit's `typos` gate today (7 errors) and probably MD060; `references/analyses` risks the same through quoted class names |
| G08 | major | g | Beat-by-beat paraphrase of whole videos committed under MIT is closer to an abridgment than to "principles"; needs an owner decision and an ADR sentence |
| G09 | major | h, i | M2 has no numeric pass criteria for the refuter, the census or the framework-only test, and the census cannot use map 02 as stated |
| G10 | major | a | Narration voice (judgment item 5) is unhandled: no derivation or check of prose rules under the paraphrase-only constraint |
| G11 | minor | b, c | Chapter 6 release scope omits `embedding.py:2232-2566`, which map 02 assigns to chapter 6 |
| G12 | minor | c, h | "The eight scripts" versus nine (`storyboard_check.py` missing from the components table); `selftest.py` covers neither it nor `frames.py` nor `render.py` |
| G13 | minor | c, i | "About twelve helpers" versus fifteen names listed |
| G14 | minor | c | "30 fps everywhere" versus the 15 fps draft tier |
| G15 | minor | c, d | `requirements.txt` pins `kokoro==0.9.4` (PyPI, Python under 3.13) while assumption 1 installs from GitHub on 3.13; the pin also forces torch on ElevenLabs-only users |
| G16 | minor | c | `lesson.py` "reads only audio, duration_s, marks_s and tail_s" but `beat()` calls `add_subcaption`, which needs `narration` |
| G17 | minor | i | "0.25 s (tightened after M0)", "when its context grows long" and three differently bounded retry loops are each readable two ways |
| G18 | minor | c | "Motion items are scored from contact sheets only" but none of the 14 rubric items is a motion item; no camera or micro-timing item either |
| G19 | minor | b | Three citations present inferences or different vocabularies as map facts (`kind` list, "timing resolved in the edit", chapter-6 file mapping) |
| G20 | minor | b, f | `TexTemplateLibrary.default` and `TexTemplate()` differ; `threeb1b` pulls fonts-extra-class packages whose install cost is unstated |
| G21 | minor | d | Alignment dynamic program plus figure bridge for a two-video release, when a reader's anchors are already budgeted |
| G22 | minor | f | "One `manim` process per scene" does not say concurrent; four CPUs are idle otherwise |
| G23 | minor | e | `evals/**/*.md` is markdownlinted; skill-creator grader and prompt files need an H1 and fenced languages |
| G24 | minor | e | jscpd counts JSON and YAML fixtures against a small denominator |
| G25 | minor | g | Provider output-usage terms (ElevenLabs tiers) unverified and the report does not record provider, voice and model |
| G26 | minor | b | Mark alignment assumes provider tokens are digit-expanded words; Kokoro tokens may keep "784"; make it provider-specific |
| G27 | minor | i | Description style deviates from the writing-skills rule the brief names; conscious, but the owner should confirm |
| G28 | minor | a | Rubric item "question before answer" has no helper or device after Pi creatures were dropped |
| G29 | minor | h | `frames.py` perceptual-distance threshold and `opening_state` semantics undefined |
| G30 | minor | d | `fetch-captions` needs `yt-dlp-ejs` and a JS runtime; not in the corpus requirements |
| G31 | minor | i | "Section" is banned at run time but used for transcript spans in the analysis schema without saying so |
| G32 | minor | f | M0 assumes a Python 3.12 venv; the container defaults to 3.13 but ships 3.11 and 3.12, which M0 should name |

## Major gaps

### G01. Mark authorship is undefined

Section 3 makes the script stage the only writer of `narration`, and marks
live inline in that text as `<mark name="x"/>` (section 8). The storyboard
stage writes `lands`, whose entries name marks. So either the scriptwriter
places marks before any visual exists, guessing where animations will land,
or the storyboarder edits `narration`, breaking the single-writer rule. The
error table's row "Mark word not found: scriptwriter rewrites the beat"
implies the first reading but never says so, and the storyboard critic has
no rule for "a `lands` entry names a mark that is not in the text".

Suggestion: give marks their own field written by the storyboard stage
(`marks: {name: word_index}` or allow the storyboarder to insert tags into a
`narration_marked` copy), keep `narration` as the scriptwriter's clean text,
and let `narrate.py` hash the clean text so a mark edit never re-synthesizes
audio. State in section 7 step 4 that `storyboard_check.py` rejects a `lands`
entry whose mark does not resolve.

### G02. The sync gate cannot fail for drift

`assemble.py` "places each beat WAV at the beat's start offset from the
index" (section 8) and `verify.py` checks "beat audio within 0.25 s of its
rendered start" (section 2). Both numbers come from the same section index
(`combine_to_section_videos`, CE `scene_file_writer.py:966-985`, with
`duration` and `nb_frames` from `get_video_metadata`, CE
`manim/utils/commands.py:47`), so the gate is an identity check. The proposal
itself lists exactly this as a cost of Approach C ("a sync gate that compares
the JSON index against offsets computed from the same index",
`architectures/minimal-viable.md:453-472,695`) and then carries the mechanism
over without change. What can actually drift is the beat's audio length
versus its rendered section length (overruns allowed up to 1.0 s) and the
mark time versus the visual, and neither is measured by this gate.

Suggestion: have `NarratedScene.beat()` append `(beat_id, Scene.time at
entry, Scene.time at exit, audio duration, overrun)` to a run log
(`Scene.time` exists, CE `scene.py:286-288`, and is frame-quantized, CE
`cairo_renderer.py:210`), and make `verify.py` compare that log to the
section index and to the WAV durations. Keep the container-duration check.
The selftest's "shifted WAV that must fail" then has a gate to fail.

### G03. One base class cannot serve 2D, camera and 3D scenes

Section 2 ships a single `NarratedScene` imported by the generated
`lesson.py`; section 6 ships `zoom_to` (needs `self.camera.frame`, so
`MovingCameraScene`) and `orbit_with_hud` (needs `set_camera_orientation` and
`add_fixed_in_frame_mobjects`, so `ThreeDScene`). In CE 0.22.0 these are
sibling subclasses of `Scene` (`moving_camera_scene.py:104`,
`three_d_scene.py:31`) with different camera classes (`MovingCamera`,
`ThreeDCamera`, `camera/*.py`). Eval prompt T2 ("one orbit") therefore
cannot be rendered by the class the design describes. Map 04's own
translation rows say the same ("you must subclass `MovingCameraScene`").

Suggestion: define `NarratedMixin` plus three concrete classes
(`NarratedScene`, `NarratedCameraScene`, `Narrated3DScene`), add a storyboard
field `scene_kind: flat | camera | 3d` written by the storyboarder and
checked by `check_scenes.py` against the class's bases, and note in
`manimce.md` that a scene cannot both zoom in 2D and orbit in 3D.

### G04. Packaging: import path undefined and the gitignore hides the runtime

Two related holes. First, `lesson.py` lives in the consumer project at
`mtv/<slug>/` and imports `mtv.narrated`, but the package is installed at
`$HOME/.agents/skills/manim-teaching-video/scripts/mtv/`; nothing says how
`manim` finds it (`PYTHONPATH` set by `render.py`, a `sys.path` line emitted
into `lesson.py`, or an editable install). Second, section 11 adds `mtv/` to
the kit's `.gitignore`. A gitignore directory pattern without a leading slash
matches at any depth, so this ignores the shipped package too. Verified in a
scratch repository: with `.gitignore` containing `mtv/`, `git check-ignore -v`
reports `skills/x/scripts/mtv/__init__.py` as ignored by that line, and
`git add -A` stages nothing but the `.gitignore`. The installer change in
section 11 would then ship a skill whose `scripts/mtv/` never reached the
repository, and the CI smoke test (`test -f` on "one script") would not
notice unless that script is inside `mtv/`.

Suggestion: anchor the pattern (`/mtv/`) or rename the run directory to
something that is not the package name; have `render.py` run `manim` with
`PYTHONPATH` set to the skill's `scripts/` directory and record that path in
`lesson.json`; make the smoke test assert `scripts/mtv/narrated.py`.

### G05. No asset, data or font policy

The example `lesson.json` (section 3) has the storyboard say "a digit image
upper left" and `introduces: ["network"]` with a 784-16-16-10 network. The
design has no step that acquires or generates images, no dataset policy, no
`ImageMobject` rule, and no statement of what `LayeredNetwork` draws for
activations. Map 02 section 11 and map 03 section 1.4 both show that 3b1b's
own scenes depend on assets absent from his repository; the skill needs its
own answer. Fonts are the same: `look.py` sets a "font default" and
`preflight.py` checks "fonts", but neither names the font, the fallback when
CMU Serif is absent (it is not a default Linux font; map 03 section 7 marks
availability unverified) nor what the frame critic should see.

Suggestion: a one-paragraph v1 policy in section 6: vector-only visuals,
seeded synthetic data (the 2026 `transformer_render.py` precedent, map 02
section 10 item 8), no raster assets, no network downloads at render time;
`look.py` tries a named serif list and records the font actually used in
`lesson.json`; the storyboard critic rejects a `visual` that names an image.

### G06. The eval plan is unbudgeted

Section 10's pass rule is "all four prompts clear every objective grader
over three runs each" with and without the skill, at the full tier (draft
render). That is 24 pipeline runs per GREEN or REFACTOR iteration, each a
Kokoro pass, several subagent waves, a 480p15 render, an assembly and a
grading pass, while render throughput and Kokoro real-time factor are
unmeasured (open questions 1, 2, 11). The reliability judgment raised eval
wall-clock explicitly; the proposal answers with a cheap inner tier but keeps
the full-tier count for the pass rule, and M3 is budgeted at three to four
days without a per-run number.

Suggestion: define the inner loop as storyboard plus `check_scenes.py` plus
`--dry_run`; one full-tier run per prompt during GREEN and REFACTOR; three
runs per prompt once, at release; run prompts concurrently; and make M0
produce the per-run wall clock that M3's budget is derived from.

### G07. Committed research fails a CI gate today

Section 11 commits the seven maps, three architectures, three judgments and
this proposal under `docs/research/manim-teaching-video/`. The hygiene job
runs `typos`, markdownlint and lychee over the whole checkout (map 06
section 3), and ADR-0006 forbids relaxing the configs. Running `typos` with
the kit's config over the design directory reports seven errors: four in map
01 (lines 24, 101 and 274, two upstream identifiers that misspell
"propagation", which map 01 itself warns about in its preamble) and three in
map 02 (lines 166 and 974, three misspelled upstream class names). Maps 01
and 07 also use the `|---|---|` separator style in 11 and 7 tables; map 06
section 3.1 reports that style is flagged by MD060 under the CI-pinned
markdownlint 0.41.1 (the only markdownlint cached here is 0.38.0, which does
not implement MD060, so this part is unverified but expected). The risk row
"Kit gates reject bundled content" covers `references/` only.

The same hazard reaches `references/analyses/`: the census requires a record
for every `spine` and `support` class and `cite_check.py` validates class
names against AST spans, so chapter 1's `NetworkMobject` keys and any
misspelled class name would be quoted verbatim. Only identifiers containing
a dictionary misspelling trip `typos` (the probe showed the "propagation"
pair fails while the "mystery" class name at `attention.py:1453` passes),
so the exposure is small but real.

Suggestion: before the PR, fix the maps (describe misspelled identifiers by
file and line, never by name, and convert separators to `| --- |`); add a
rule to the analysis schema that `class` names are stored but misspelled
ones are never rendered into `references/analyses/*.md` prose (cite line
numbers instead); run the pinned markdownlint and `typos` in the worktree
before every commit, as section 11 already promises for `skills/`.

### G08. License granularity of the committed analyses

Section 5's record stores, for every aligned section of a video, a
40-to-120-word paraphrase of the narration, a per-beat `narration_gist`, a
per-beat `visual` description, timing and the question planted. For a
19-minute video that is a beat-by-beat abridgment of the narration and the
staging. Map 06 section 6 and map 07 section 6 allow "principles derived
from study, original ManimCE code, citations and short attributed quotes;
no transcript dumps" in the MIT kit, because CC BY-NC-SA's ShareAlike and
NonCommercial terms cannot attach to MIT content. The 13-word verbatim guard
prevents copying but not abridgment, and the brief's fixed decision covers
code, not narration. This is a judgment call the owner, not the implementer,
should make; the proposal's risk table rates "license leakage" low with
"paraphrase only" as the mitigation and does not surface the question.

Suggestion: present two options in "Decisions needed": (A) analyses stay in
the corpus repository under CC BY-NC-SA and the kit ships only
`framework.md`, `patterns.md`, `rubric.md` whose rules cite video id,
timestamp, file and line; or (B) analyses ship in the kit with an explicit
statement in ADR-0008 (or a separate ADR-0009) of why factual descriptions
are not an adaptation. Either way the attribution note moves from
`framework.md` alone to every shipped reference derived from the corpus.

### G09. M2 has no numeric pass criteria

M2 "proves" that the framework rests on checked evidence, but: the refuter
"tries to disprove three random claims per record" with no stated tolerance
(how many disproved claims fail a record or a video); `census.py` checks that
the tag histogram "agrees" with grep counts with no tolerance; and the
framework-only storyboard test has no threshold, unlike the rubric
calibration (24 of 28) and the rule discrimination test (pass or rewrite).
The census also cannot be computed as written for chapter 6: map 01 section
9 gives per-file counts for `part1.py`, but map 02 section 5.1 gives "lines
containing the pattern" summed over ten files, with per-file counts only for
`play`, `wait`, `reorient` and `fix_in_frame` (map 02 section 9.1). The
corpus `scenes` step must produce its own per-file counts.

Suggestion: refuter pass is zero disproved claims per record (a disproved
claim returns the record); census tolerance is stated as a ratio (for
example tag count at least 30 percent of the idiom's per-file line count);
the framework-only storyboard test passes at the rubric floor (22 of 28);
and the `scenes` step emits per-class idiom counts that `census.py` reads
instead of the maps.

### G10. Narration voice is unhandled

The animation judgment's fifth unhandled item is that paraphrase does not
carry voice, so no design says how narration-voice rules (second person,
planted questions, hedges, sentence length per beat, the "honest lie" and
admitted uncertainty) are derived or checked. The proposal's framework has a
"narrative" and an "honesty" group, but the scriptwriter reads
`framework.md` only, nothing in the corpus tools computes narration
statistics, and the rubric has one narration-adjacent item ("honesty beat").
For a skill whose output is a narrated video, the script is half the
product.

Suggestion: have the corpus `align` step emit per-video narration
statistics that are facts, not text (words per beat, questions per minute,
hedge-phrase rate, mean sentence length, pronoun person, first-formula time
as a fraction of runtime), store them in the analysis record, derive three
to five narrative rules with numeric `Apply` predicates that
`storyboard_check.py` can evaluate on the script, and add one rubric item
for voice with anchors.

## Minor gaps

### G11. Chapter 6 scope omits part of embedding.py

Section 4 defines the chapter 6 release scope as `attention.py` plus
`supplements.py:841-1338`. Map 02 section 1.1 assigns three chapter-6
scenes to `embedding.py:2232-2566` (`MultipleMoleEmbeddings`,
`RefineTowerMeaning`, `UpdatingPoetryEmbedding`). The census will either
miss them or flag them. Add the range, or state that embedding inserts are
out of scope and tell the census so.

### G12. Script count and self-test coverage

The components table lists eight scripts and M1 says "the eight scripts";
section 7 step 4 and the repository layout add `storyboard_check.py`
(nine). `selftest.py` covers schema, `check_scenes.py`, `narrate.py`,
`assemble.py` and `verify.py`; `storyboard_check.py`, `frames.py` and
`render.py` have no test. Add the ninth script to the table and give the
three untested scripts at least a fixture test (a synthetic storyboard, a
synthetic clip, a fake `manim` executable).

### G13. Helper count

Section 2 says twelve helpers; section 6 lists fifteen names (three nouns,
three provenance, three emphasis, two numbers, two camera, two narration).
Pick a list and a number; `selftest.py --patterns` renders one example per
helper, so the count is a test budget.

### G14. Frame rate statement

The risk table says "30 fps everywhere" while assumption 3 and section 2
define the draft tier at 15 fps. Say "30 fps at `standard` and `final`".

### G15. Kokoro pin versus Python 3.13 path

`requirements.txt` pins `kokoro==0.9.4`, whose PyPI metadata is
`requires_python <3.13,>=3.10` (verified from the cached record), while
assumption 1 installs Kokoro from GitHub on 3.13. `pip install -r` on 3.13
fails before `preflight.py` can print the GitHub line. The pin also drags
torch, transformers and spaCy into every install, including ElevenLabs-only
ones. Split into a base file and a `requirements-kokoro.txt`, and let
`preflight.py` choose the install line by interpreter version.

### G16. `lesson.py` input fields

Section 3 says the generated `lesson.py` "reads only `audio`, `duration_s`,
`marks_s` and `tail_s`", but section 8's `beat()` calls `add_subcaption`,
which needs the beat's `narration`. Add it to the list, or have `narrate.py`
write the clean text into `words.json` and read it from there.

### G17. Readings the owner cannot disambiguate

Three phrases admit two readings: "within 0.25 s of its rendered start
(tightened after M0)" (is 0.25 s the value before or after tightening?);
"when its context grows long it stops" (no observable trigger: number of
stages, number of dispatches, or a token estimate); and the retry bounds
"two rounds, then ask" (storyboard), "at most two passes" (fix loop), "three
attempts per scene, then simplify once, then stop" (render exceptions) sit
in three sections. Put all bounds in one table in section 9 with the value
that applies before M0 and the field in `lesson.json` that counts them.

### G18. Rubric items without a mechanism

Section 6 says "Motion items are scored from contact sheets only", but the
fourteen listed items contain no item about motion (easing, travel arcs,
stagger, nothing teleporting), and none about the camera or micro-timing
inside a `play`, which the animation judgment flagged against Approach C's
rubric. Either add one motion item with anchors (and keep contact sheets as
its input) or delete the sentence and the contact-sheet step.

### G19. Citation looseness

Three statements cite a map for something the map does not quite say.
Section 5 attributes the `kind` vocabulary (`spine`, `support`, `overlay`,
`ambient`, `thumbnail`, `end_screen`, `stub`, `utility`) to map 03 section
4.3, which proposes `main`, `overlay`, `ambient`, `thumbnail`, `end_screen`.
Section 1 states "3b1b resolves timing in the edit (map 03 section 6)",
which map 03 marks as an inference from code with the recording order
unverified. Section 4's chapter-6 file mapping is marked "inferred" in map
07 section 3 and stated as fact. Mark the inferences or cite the proposal's
own choice.

### G20. TeX template facts and install cost

The proposal correctly selects `TexTemplateLibrary.threeb1b`
(`tex_templates.py:67`, with `add_to_preamble` at `tex.py:91`). Two things
should reach `manimce.md`: `TexTemplateLibrary.default` is also the 3b1b
preamble (`tex_templates.py:64`) while `TexTemplate()` with no arguments is
the three-package preamble (`tex.py:21-23,50`), which is what an empty
`tex_template` key yields (`default.cfg:144`), so map 04's sentence "the
default preamble is the 3b1b preamble" is true only of the library
constant. And `threeb1b` loads `calligra`, `tipa`, `wasysym`, `dsfont`,
`physics` and `mathrsfs`, which on Debian-family systems means
`texlive-fonts-extra` and `texlive-science` (the package list 3b1b's README
names, map 03 section 1.3), a multi-gigabyte install the preflight message
should name and the assumptions should cost.

### G21. Alignment machinery for two videos

Section 4 builds a monotonic dynamic program over string literals, class
names and a figure bridge, then still budgets a reader adding three to six
anchors per video. For a two-video release where chapter 1 is one file in
definition order, a reader can section the whole video in the same thirty
minutes. Keep the DP as the M5 extension and ship M2 with reader-made
sections plus `cite_check.py`, or at least drop the figure bridge from M2.

### G22. Concurrency of per-scene renders

"One `manim` process per scene" (sections 2 and 9) does not say the
processes run concurrently. On four CPUs a sequential render leaves three
idle; Cairo is single-threaded per scene and encoding can overlap
(`max_inflight_encoders`, map 04). Add `render.py --jobs N` with a default
of CPU count minus one, and let M0 measure both settings.

### G23. Eval markdown under the linter

`.markdownlint-cli2.jsonc` has no ignores, so `evals/**/*.md` is linted (map
06 section 3.1). skill-creator grader files are a frontmatter block and one
sentence (map 06 section 5.2), which fails MD041 without an H1, and
`prompt.md` settings blocks need a fenced language for MD040. Say that every
eval markdown file opens with an H1 and fences name a language, or extend
the one-line `validate.sh` exclusion idea to the markdownlint config, which
ADR-0006 forbids.

### G24. jscpd denominator

jscpd tokenizes Python, shell, YAML and JSON and fails above 5 percent
duplicated tokens (map 06 section 3.4). The kit has little code today, so
the denominator is small, and `lesson.example.json`, several
`evals/*/case.yaml` files and any JSON fixture that repeats the lesson
header will be near-duplicates. The proposal generates selftest fixtures in
code (good); say the same for eval `case.yaml` boilerplate (a template
rendered by a script) or accept one more `common.py` style consolidation.

### G25. Provider output terms and the report

Kokoro weights are Apache-2.0 (verified from the cached PyPI license text).
ElevenLabs and OpenAI usage terms for generated audio depend on tier and
could not be fetched (map 05 section 9). Section 7's report lists path,
duration, tier, rubric totals, gates, render time and resume, but not the
provider, voice and model, which is what a user needs to check their own
rights. Add those three fields to `report.md`; the Piper opt-in note already
implies the mechanism.

### G26. Token normalization is provider-specific

Section 8 normalizes script words with `num2words` to match provider tokens.
Kokoro's `join_timestamps` attaches times to misaki tokens (map 05 section
2); whether a token for "784" carries the text "784" or expanded words is
unverified, and ElevenLabs returns both `alignment` and
`normalized_alignment`. Make the matcher a per-provider function in
`mtv/tts.py` with a fallback to proportional interpolation, and list the
Kokoro token text format as an M0 measurement.

### G27. Description style is a conscious deviation

The brief's check (e) names "description = triggers only" (the
writing-skills rule). The proposal follows map 06 section 5.1's resolution
instead: kit style, capability plus trigger phrases, no workflow summary.
That is defensible and matches `skills/research/SKILL.md:2-9`, but it is a
deviation from a rule the brief names, so list it under "Decisions needed"
rather than in section 7 only.

### G28. The learner-objection beat has no device

Pi creatures are correctly out (map 03 section 2.6), and rubric item
"question before answer" remains. Approach A had an original replacement
(`PT-42 question-caption-with-arrow`, `PT-43 learner-objection-callout`,
`architectures/corpus-fidelity.md:396`); the proposal's fifteen helpers
have none. Add one `question_caption` helper or state the storyboard device
the rule expects.

### G29. Continuity check parameters

`frames.py` flags "perceptual distance above threshold" at scene boundaries
and `opening_state` not `black`. The threshold, the metric (hash distance or
pixel difference at what resolution) and the semantics of `closing_state`
versus `opening_state` strings (free text for the coder, or a structured
list the checker parses) are undefined. Say which, and add calibration to
M1's hand-written lesson, which has two scenes by construction.

### G30. yt-dlp runtime prerequisites

Map 05 section 4 says YouTube extraction now needs `yt-dlp-ejs` plus a JS
runtime (`--js-runtimes node`, which the table already passes). Add
`yt-dlp-ejs` and Node to the corpus repository's requirements.

### G31. "Section" on the corpus side

Section 1 bans "section" for storyboard units at run time. Section 5's
analysis schema uses `section_id` for transcript spans. That is fine, but
say so in the vocabulary paragraph so the two halves do not look
inconsistent.

### G32. Python versions for M0

M0 says "a venv on Python 3.12". The implementation container defaults to
3.13.17 (map 05) but has `/usr/bin/python3.11`, `/usr/bin/python3.12` and
`uv` (verified here). Name the command (`uv venv --python 3.12`) so M0 does
not stall on an interpreter hunt, and record that this closes assumption 4
for the implementation environment, not for consumers.

## Claims verified against primary sources

These statements in the proposal were checked here and hold:

1. GL `YELLOW` is `#FFFF00`, CE `PURE_YELLOW` is `#FFFF00` and CE `YELLOW`
   is `#F7D96F` (`manim/utils/color/manim_colors.py:156,178,181`).
2. Section MP4s carry no audio: `combine_to_section_videos` concatenates
   partial movie files only (`manim/scene/scene_file_writer.py:966-985`).
3. The section index holds `name`, `type`, `video` plus `duration` and
   `nb_frames` (`manim/scene/section.py:83-103`;
   `manim/utils/commands.py:47`).
4. `disable_caching_warning` is a config key, not a CLI flag
   (`manim/_config/default.cfg:134`).
5. `Scene.time` exists and returns the renderer clock
   (`manim/scene/scene.py:286-288`); the clock advances by whole frames
   (`manim/renderer/cairo_renderer.py:210`), so the `beat()` padding against
   the absolute clock is sound and open question 2's quantization worry is
   answered: `wait(max(target_end - self.time, 1/fps))` self-corrects.
6. `run_time <= 0` raises and sub-frame values are clamped with a warning
   (`manim/scene/scene.py:1141-1168`).
7. `DecimalNumber` digits are `MathTex` by default
   (`manim/mobject/text/numbers.py:87`), so M0's "confirm `DecimalNumber`
   needs LaTeX" is already settled and can be dropped.
8. `TexTemplateLibrary.threeb1b` exists (`manim/utils/tex_templates.py:67`)
   and `TexTemplate.add_to_preamble` exists (`manim/utils/tex.py:91`).
9. `manim` 0.22.0 requires Python 3.11 or newer; `kokoro` 0.9.4 requires
   Python 3.10 to 3.12 with an Apache-2.0 license; `elevenlabs` 2.74.1 and
   `soundfile` 0.14.0 are current (cached PyPI JSON).
10. Numbers attributed to the architectures are present as quoted: 19
    sessions and 44 patterns (`corpus-fidelity.md:386,744`), 19 to 24 days
    and the `wait()` ban (`repeatable-process.md:458,812`), nine to ten days
    and the circular drift gate (`minimal-viable.md:453-472,682,695`).
11. The proposal passes markdownlint 0.38.0 with the kit's config and
    `typos` with the kit's config (0 errors each); its five bare links are
    canonical GitHub or PyPI pages.
12. All three judgments' tie-break notes name the same hybrid the
    recommendation adopts.

## Unverified or blocked

1. MD060 behavior under markdownlint 0.41.1 on maps 01 and 07 (only 0.38.0
   is available here; map 06 section 3.1 reports the failure from its own
   run of the pinned version).
2. Kokoro token text for numerals and the real-time factor (map 05 marks
   both low confidence); ElevenLabs and OpenAI output-usage terms (vendor
   pages blocked).
3. ManimCE render throughput on four CPUs; no render ran here or in any map.
4. Whether `apt-get` can reach a Debian mirror from the implementation
   container for TeX Live; the proposal's M0 assumes it.
5. Whether YouTube manual captions exist for chapters 1 and 6 (YouTube
   blocked); the proposal already marks this.
