# Judgment: animation and pedagogy practitioner lens

Reviewer lens: someone who makes and critiques explanatory animation. The
question asked of each architecture is not "will it render" but "would the
framework it produces make an agent write ManimCE that looks and teaches
like 3Blue1Brown", and "is that framework checkable rather than a list of
platitudes". Evidence below is cited to the three architecture files under
`scratchpad/design/architectures/` and to the seven maps under
`scratchpad/design/maps/` (written as map NN, section N.N). Claims I could
not trace to a map or a clone are marked unverified.

## What the corpus says makes the videos good

Before judging, a short restatement of the target, so the scores have a
fixed reference. The maps reduce the corpus to roughly thirty evidence-backed
moves (map 01 section 8, sixteen moves; map 02 section 8, fourteen moves)
plus structure (map 01 section 6, map 02 section 6.3), color contracts (map
01 section 3, map 02 section 3.1), timing distributions (map 01 section 5.2,
map 02 section 6.2) and a layout grammar (map 01 section 4, map 02 section
4). The moves that matter most to a practitioner, because they are the ones
an agent will not do by default:

1. Numbers before symbols, and symbols introduced by a transform from the
   concrete thing (map 01 section 8 move 4 and 5; map 02 section 8 move 1).
2. A working thing before any definition, and a preview of the destination
   that is then hidden (map 01 section 8 moves 1 and 2).
3. Zoom to one unit, build the formula term by term from its parts (map 01
   section 8 move 3).
4. Dim, do not delete; return to a saved layout after a digression; carry
   the picture forward into the recap (map 02 section 8 move 4; map 01
   section 8 moves 13 and 15).
5. One hue per role for the whole lesson, applied by substring (map 01
   section 8 move 9; map 02 section 8 move 2).
6. Light the path then release; give adjustable things a tremor; motion in
   the direction of meaning (map 01 section 8 moves 7 and 8; map 02 section
   8 move 9).
7. The camera as a second narrator, and micro-timing inside one play (map
   02 section 8 moves 5 and 14).
8. Honesty devices: admit what is skipped, the honest lie, the viewer's
   question voiced on screen (map 01 section 8 move 6; map 02 section 6.3
   items 3, 6 and 7).
9. Rhythm: play, wait, play, wait, a longer wait closing a step; sub-second
   montages for "many"; long holds only where narration or an orbit carries
   the moment (map 01 section 6.4; map 02 section 6.1 and 6.2).

Narration is not in the code (map 03 section 6), so every narration-level
rule must come from transcripts, which only exist once the corpus pipeline
has run.

## Corpus fidelity: scores

| Criterion | Score | Justification |
| --- | --- | --- |
| Output-quality fidelity | 9 | The 24 technique tags (section 4.2) are the union of the two moves lists and cover 21 of the 30 corpus moves; the 44-pattern library (section 5.3) is the only one that includes camera, 3D, the 2024 visual nouns, collapse-to-symbol and a `time_span` stand-in; the narration analyst records where the visual changes relative to the words (section 4.1 item 2), which no other design captures. |
| Repeatability | 7 | Per-stage artifact contracts, bounded storyboard loop, section-local re-render and an objective sync gate (sections 6.3 and 6.4), but no explicit run state or input hashing at run time, so resumption after interruption is implied rather than designed. |
| Feasibility | 5 | About 19 focused sessions with the eight-video census as a five-session long pole (section 10); three analyst roles plus two verifiers per video means hundreds of subagent runs; 44 pattern examples with committed reference frames; alignment on multi-file 2024 videos is estimated at 60 percent before anchors (map 07 section 4). The vertical slice (M1 to M2) is the right mitigation but still comes after three sessions of corpus work. |
| Corpus leverage and grounding | 10 | Citation checker that resolves every file:line against the class span and requires an animation identifier in range, refuter pass, census that reconciles tag histograms with the grep counts in map 01 section 9 and map 02 section 5.1, inter-analyst Jaccard, human anchors (sections 4.3 and 4.5). This is the only design with a defense against analysts writing from memory. |
| Kit fit and authoring practice | 7 | Follows map 06 on install.sh, `AGENT_REF`, `SLASH_REF`, ADRs and SKILL.md size (sections 6.1 and 9); RED, GREEN, REFACTOR with pressure scenarios (section 8.3). Costs: five new agents, two ADRs, two repositories, binary reference PNGs for pattern CI whose home (kit or corpus repo) is left ambiguous between sections 8.1 and 8.2. |
| Testability | 9 | Pattern CI with perceptual-hash regression proves each CE idiom renders; the rule discrimination test (compliant versus violating snippet per rule, section 8.2) is the single best idea in any of the three files for keeping rules out of platitude territory; framework-only generation test isolates the framework from the orchestrator. |
| Simplicity | 3 | 24 principles, 44 patterns, 20 rubric items, ten scripts, five agents, two repositories, three analyst roles plus two verifier roles. Section 13 item 8 admits a 25-pattern core would do. |

Total: 50 of 70.

## Corpus fidelity: strengths

- The technique-tag vocabulary is fixed before analysis so records are
  comparable, and it is the right vocabulary: it carries the moves a
  practitioner would name (zoom-to-one-unit, provenance-transform,
  knobs-tremor, light-the-path, dim-not-delete, camera-as-narrator,
  micro-timing-in-one-play, honest-lie, one-then-all).
- Principles have two `Check` lines each, one for the storyboard critic and
  one for a static lint (section 5.2). The example P04 is a real predicate:
  for each `MathTex` symbol first appearing in beat k, a numeric visual of
  the same concept exists in beats 1 to k-1. That is checkable.
- Pattern pages carry intent, when not to use, corpus evidence with a
  keyframe reference, the CE idiom with its gotchas, and the rubric items
  served (section 5.3). An agent reading one page learns the move and the
  translation at once.
- Timing defaults are pulled from distributions, not taste: 1 s rest, 2 s
  after reveals, 5 s on reaction beats, 8 to 12 s orbits, `lag_ratio` 0.1
  for crowds and 0.5 for sequential reveals (section 5.1, `timing.md`).
- ElevenLabs `previous_text` and `next_text` are mentioned for prosody across
  beats (section 7), the only acknowledgement in any design that per-beat
  synthesis produces choppy delivery.
- The `PT-43 learner-objection-callout` is an original stand-in for the
  Pi-creature reaction beat, which map 03 section 8 item 7 says must be
  replaced, not copied.

## Corpus fidelity: weaknesses

- Colors: `framework/colors.md` lists emphasis as `PURE_YELLOW` but query as
  `YELLOW` (section 5.1). In ManimGL both are `#FFFF00`; in ManimCE `YELLOW`
  is `#F7D96F` and only `PURE_YELLOW` is `#FFFF00` (map 04, constants row).
  As written, the attention chapter's most-used role color would render in
  the wrong hue. Every GL `YELLOW` in a role contract must become
  `PURE_YELLOW` in the CE contract.
- Timing: `timing.md` fixes a 2 s default `run_time`. That is the 2024
  default (map 02 section 6.2), but the 2017 series defaults to 1 s with 2 s
  reserved for writes and transforms that carry meaning (map 01 section 5.2,
  104 uses of 1 versus 71 of 2). Collapsing the two loses the faster 2017
  rhythm; the rule should be "1 s confirmations, 2 s meaning-carrying
  transforms", which both series support.
- The sync gate is symmetric ("within 0.5 s of its narration anchor",
  section 5.4) even though the narration analyst records lead and lag. The
  design collects the one signal that distinguishes "show then name" from
  "name then show" and then does not use it.
- Frame review uses the last frame and two mid-beat frames (section 6.2,
  `check_frames.py`). Stills cannot judge motion quality, which is where
  most of the 3b1b look lives (easing, travel paths, stagger).
- Beat duration bound of 4 to 40 s (section 5.4). A 40 s beat with one
  `add_sound` and one `next_section` is too coarse for the per-beat sync the
  design wants; 2024 beats end in a `wait()` after a few plays (map 02
  section 6.1), which is 5 to 20 s.
- Object budget of "about 250 primitives" has no corpus citation; map 01
  section 8 move 10 gives 16 shown neurons, 70 percent of edges removed,
  and the calculus on a 1-1-1-1 network. The number is a guess.
- Three missing moves from the 24 tags: motion-with-a-reason (map 02
  section 8 move 9, present only as a rubric line), transitions-reuse-
  geometry (move 13) and the recurring cast of examples (map 02 section 6.3
  item 8). The first two are visible in every frame and belong in the tags.

## Corpus fidelity: factual errors and unverified claims

- "117 `ReplacementTransform` provenance moves" (section 1): 117 is the
  total count of `ReplacementTransform` uses in the three 2017 files (map 01
  section 9); not all are provenance moves. Overstated.
- `lag_ratio` 0.1 for crowds is cited to "M02 section 6.2" (section 1 and
  `timing.md`); the 0.1 figure (125 lines) is in map 02 section 5.1. The
  value is right, the citation is off.
- "105 `save_state` and `restore`" matches map 01 section 5.3 (48 plus 57).
  Correct.
- `DecimalNumber(mob_class=Text)` is correctly marked unverified (section
  11), matching map 04.
- The pattern CI reference frames: whether they live in the kit (installer
  would ship binaries) or the corpus repo is not stated. Unresolved.
- Whisper real-time estimate for `large-v3-turbo` (section 3.5) is an
  extrapolation from map 05 section 4, which itself is low confidence.
  Unverified.

## Corpus fidelity: ideas worth grafting

1. The rule discrimination test: one compliant and one violating storyboard
   snippet per rule, graded by a critic holding only the rule text; a rule
   that does not separate them is rewritten.
2. The census that compares per-video technique-tag histograms with the grep
   counts in map 01 section 9 and map 02 section 5.1.
3. The narration analyst's lead/lag record, which should feed a signed sync
   offset in the storyboard.
4. The six-group pattern taxonomy (nouns, provenance, emphasis, numbers,
   camera, narration) as the shape of the library even if fewer patterns
   ship first.
5. The two-`Check` rule form (storyboard predicate plus static lint).

## Repeatable process: scores

| Criterion | Score | Justification |
| --- | --- | --- |
| Output-quality fidelity | 6 | The storyboard schema (section 6.4) with `introduces`, `shows_value_of`, `symbol_introduced` and `sync` makes the two most important pedagogy rules statically checkable; but section 12 item 1 cuts 3D and camera work entirely, which removes the 2024 series' visual grammar (139 `reorient` calls, "camera as a second narrator", map 02 sections 4.2 and 8), the 24 patterns omit most 2024 nouns and the collapse-to-symbol idiom, and `check.py` bans `wait()` inside a beat (section 6.3 item 6), which forbids the corpus's dominant rhythm. |
| Repeatability | 9 | Eight gates each with a code or rubric check, `state.json` with input hashes, one `manim` process per scene, bounded loops with named escalations, and a hard rule that a file failing `verify.py` is never delivered (sections 6.2, 6.5, 6.6). Word-index bookmarks (section 6.4) are brittle under script edits. |
| Feasibility | 6 | 19 to 24 session days, the largest estimate; no 3D reduces render risk; `text_only` engine mode is thoroughly specified (section 6.6); M3 cannot start before four analysis records exist (section 10). |
| Corpus leverage and grounding | 7 | `check_analysis.py` resolves citations and tests a 12-word verbatim leak, refutation pass, cross-video vocabulary convergence, coverage rule (sections 4.3 and 4.4). But one analyst per transcript section (section 4.1) cannot see cross-section devices (carry the picture forward, pipeline stays on screen, save and restore after digression), and the record schema has no lead/lag field. |
| Kit fit and authoring practice | 8 | Explicit compliance with map 06 on paths, installer, `AGENT_REF`, jscpd via one `common.py`, fixtures generated at test time, `CONTEXT.md` vocabulary (section 9); RED baseline must fail at least four of six objective graders or "the skill adds nothing measurable" (section 8.3 item 5), which is the honest version of GREEN. |
| Testability | 9 | `selftest.py` runs without ManimCE and adds `--patterns` and `--one-beat` with it (section 8.1); conformance eval on five sections before the skill exists (section 8.2); six eval topics including a non-math one; two-judge agreement for final tiers (section 11). |
| Simplicity | 5 | Eight gates, ten scripts plus five provider modules, five agents, 18 rubric items; cleaner than corpus fidelity, still a large surface for a first release. |

Total: 50 of 70.

## Repeatable process: strengths

- Narration-first with a static overrun guard: `check.py` rejects a beat
  whose declared `run_time`s exceed the audio length minus 0.3 s (section
  7.4), so a beat can never push later beats late. No other design has a
  pre-render timing check.
- Frames are extracted at bookmark times, where the sync claim is made
  (section 6.3 item 7), and the runtime writes a bounding-box log at the end
  of each beat, so clipping is caught by code rather than by vision.
- Rules carry Apply, Check, Why and Fails (section 5.2); the Fails line is a
  concrete counterexample ("a storyboard whose first beat writes
  `a = sigma(Wx + b)`"), which is what a critic needs to recognize a
  violation.
- Rubric group V includes "motion direction matches data flow" and "text
  legible at 480p" (section 5.4), two things a practitioner checks first.
- The error table from map 04 is matched by regex and the row's fix text is
  injected into the coder's retry prompt (section 6.6).
- The `text_only` engine lists exactly which classes are forbidden without
  LaTeX (section 6.6), matching map 04's dependency list.

## Repeatable process: weaknesses

- Cutting 3D and camera moves (section 12 item 1) is a fidelity decision,
  not a scope decision. The brief's corpus includes the transformer series,
  whose stage is 3D by default (map 02 section 10 item 3) and whose camera
  is one of the fourteen moves. The framework will then describe a device
  the pattern library cannot execute; the storyboarder will either violate
  the framework or write 2D stand-ins with no corpus precedent.
- Banning `wait()` inside beats and padding only at the beat's end (sections
  6.3 and 7.3) front-loads every beat: animations fire back to back, then
  silence. The corpus rhythm is play, wait, play, wait, longer wait (map 01
  section 6.4: 423 waits for 795 plays). The `until(mark)` helper can
  substitute, but only if the storyboard puts a bookmark at every pause,
  which the design does not require.
- Per-section analysts (section 4.1) are given one section's transcript and
  the aligned classes. Spine scenes run 500 to 1,500 lines and span several
  transcript sections (map 01 section 1.4), so the analyst sees a slice of
  a scene and cannot report the scene's layout discipline, its save and
  restore returns, or what it carries into the next section. The "cheaper
  video-level merge" is asked to recover exactly the devices the slices
  hide.
- The pattern list (section 5.3) has no collapse-to-symbol pattern, which
  is map 02 section 8 move 1 and the central numeric-to-symbolic device of
  the 2024 series; `formula_build` and `provenance_transform` cover part of
  it but not the bracket squash.
- Rubric N "speech rate 140 to 170 words per minute" (section 5.4) is not a
  measured 3b1b property; the 150 to 170 figure in map 07 section 5 is an
  estimation basis for transcript size. Unverified as a quality criterion.
- Bookmarks as word indices (section 6.4) break whenever the scriptwriter
  edits a sentence; corpus fidelity's substring anchors are more robust.

## Repeatable process: factual errors and unverified claims

- "lock file on ManimCE 0.20.1" for manim-voiceover (section 7.3): matches
  map 05 section 1 (`uv.lock` resolves 0.20.1). Correct.
- "ManimCE 0.19+ encodes with PyAV" (section 6.3 item 2): matches map 04.
  Correct.
- `max_inflight_encoders = 4` (section 6.7): matches map 04, which quotes
  "4 is a good value on typical hardware". Correct.
- Pi-creature scenes "tagged `interstitial` (map 03 section 4.3 `kind`
  field)" (section 4.4 item 4): map 03 section 4.3 proposes `kind` values
  `main`, `overlay`, `ambient`, `thumbnail`, `end_screen`; `interstitial`
  is not among them. Minor vocabulary drift.
- Render budget constants (draft 5 minutes, standard 40, uhd 3 hours,
  section 6.6) are stated as unverified until M0 measures. Correctly
  flagged.
- "3b1b uses 30 fps" (section 6.3 item 8): map 03 section 1.1. Correct.

## Repeatable process: ideas worth grafting

1. The storyboard fields `introduces`, `shows_value_of`,
   `symbol_introduced`, `bookmarks` and `sync`, which make numbers-before-
   symbols and sync claims checkable before any audio or code exists.
2. The static overrun guard and the runtime bounding-box log.
3. Frames at bookmark times rather than at arbitrary mid-beat positions.
4. `state.json` with input hashes and the rule that a failed `verify.py`
   never ships.
5. The GREEN definition that requires the baseline to fail objective
   graders.

## Minimal viable: scores

| Criterion | Score | Justification |
| --- | --- | --- |
| Output-quality fidelity | 6 | The ten helpers (section 5.3) are well chosen and include `numbers_to_symbol`, `count_parameters`, `delayed` and one orbit, and `look.py` ships `PURE_YELLOW` and the richer `TexTemplate`; but the first-release framework rests on code-only maps plus two videos, so narration-level rules have almost no transcript evidence; the twelve-item rubric has no camera, micro-timing or motion-direction item; and rubric item 8's "no hold over 4 s without motion" (section 5.4) contradicts the corpus's deliberate 5 to 30 s holds (map 01 section 6.4; map 02 section 6.2). |
| Repeatability | 7 | One contract with single-writer fields makes resume trivial (section 2.3) and hard gates are objective (section 5.4); but stages rerun only when outputs are missing, not when inputs changed, so a stale `lesson.py` after a storyboard edit is not detected; fix loop stops after two passes. |
| Feasibility | 9 | M0 is a hand-written two-beat spike before any corpus work (section 10), the one thing every practitioner would do first; audio is muxed by section offsets outside Manim so voice changes never re-render (section 7.3); nine to ten days; no new agents. |
| Corpus leverage and grounding | 4 | Two videos at release; one analyst per video, which the design itself says overflows on a 25-minute video (section 4.1) while chapter 6 is one of the two pilots; bucket figures stand in for keyframes; the refuter samples ten claims; no census or histogram reconciliation. |
| Kit fit and authoring practice | 9 | Three single-expression kit changes, no `AGENT_REF` change, inline role prompts as the kit's own research skill allows (map 06 section 4.1), one ADR, headings fixed for MD024 (sections 4.2 and 9.2). |
| Testability | 7 | Pytest per unit boundary including a rendered two-beat `NarratedScene` and an assemble-plus-verify fixture (section 8.1); framework test before the skill exists (section 8.2); but only three topics, no pattern regression images, no rule discrimination test. |
| Simplicity | 9 | One contract, six scripts, a 400 to 600 line helpers module, twelve rubric items, five inline roles. |

Total: 51 of 70.

## Minimal viable: strengths

- The M0 spike targets the right unknowns: sections padded to narration,
  `--save_sections` JSON index durations, Kokoro real-time factor, CPU
  render throughput (section 10). None of these were executed in the design
  container and all three designs depend on them.
- "Imported, not recalled" (section 11): shipping the idioms as functions in
  `patterns.py` attacks the ManimGL-from-training-data failure directly,
  and `check_scenes.py` rejects the GL names and the `play(mob.method)` form
  before any render (section 6.2 item 5).
- Rubric item 7, "each beat's visual changes when the narration's subject
  changes", is checked by `verify.py` from word timestamps against section
  boundaries (section 5.4). That is an objective proxy for a pedagogical
  property and the only one of its kind in the three designs.
- `look.py` names the preamble packages (`dsfont`, `mathrsfs`, `physics`,
  `xcolor`) and the `PURE_YELLOW` swap in shipped code (section 5.1), so the
  look is a dependency, not a reminder.
- Eval T3 (softmax, a 2024 topic without the 2024 helpers) tests whether the
  rules transfer beyond the helpers (section 8.4).
- Rules have a SCOPE line with a stated exception (section 5.2), which
  prevents a critic from penalizing a recap for showing a known symbol.

## Minimal viable: weaknesses

- Rubric item 8 as written would penalize a 15 s orbit hold, a 5 s reaction
  beat and the chapter-2 dots rolling downhill (map 02 section 6.2; map 01
  section 6.4). The corpus rule is "long holds only where narration, an
  orbit or ambient motion carries the moment"; the design's own R25/R26
  text ("long holds only with motion or narration", section 5.2) is right
  and the rubric line should say the same.
- The first-release framework is derived from maps written from code with
  no transcript (map 01 section 6.4 says narration is not in the code), so
  the Narrative group of rules (hook, plan preview, question before answer,
  hedging) has evidence only for on-screen text, not for what is said.
  Chapter 1 and 6 transcripts will arrive in M2, after `framework.md` v0 is
  drafted; the design should say v0 narrative rules are provisional.
- One analyst per video for chapter 6 (attention.py plus a supplements
  block, section 3.1) is the case the design says needs per-section
  fan-out (section 4.1). The pilot therefore exercises the weakest analysis
  configuration on the hardest file.
- No camera rules or patterns beyond one orbit; the 2024 nouns are deferred
  (section 5.3). Reasonable for a first release, but the framework test
  (section 8.2) will then never exercise the camera-as-narrator move, and
  T2 ("a 3D orbit") has one helper and no rule to judge it by.
- `b.until("digits")` returned as a `run_time` (section 6.2 item 5) will be
  zero or negative when the word has already passed; nothing in the design
  guards it.
- Frame review is two stills per beat (section 6.3), the same motion
  blindness as the other two designs.

## Minimal viable: factual errors and unverified claims

- "the useful core is about 400 lines under MIT" for manim-voiceover
  (section 7.4): map 05 section 1 gives `voiceover_scene.py` at 238 lines
  plus `tracker.py` and parts of `base.py`; 400 is a plausible sum but not
  stated anywhere. Unverified.
- "needs `--disable_caching`" (section 7.4): map 05 lines 63 and 164.
  Correct.
- `--disable_caching_warning` as a CLI flag (section 6.2 item 6): map 04
  documents `disable_caching_warning = True` as a config key; the CLI flag
  spelling is not verified in the maps. Unverified.
- "`supplements.py` block at lines 841 to 1338" for chapter 6 (section 3.1):
  map 07 section 3. Correct.
- "80 to 90 percent for one-file videos" (section 3.1): map 07 section 4.
  Correct.
- "one spine scene per 2 to 4 minutes (map 01 section 1.4)" (section 6.2
  item 1): map 01 section 1.4 names five spine scenes across three files but
  gives no per-minute density. Unverified.
- "roughly 1900 lines before the first weighted sum" (section 5.2): map 01
  section 6.2 says the working classifier and the "neuron holds a number"
  idea precede the first weighted sum by about 1900 lines. Correct in
  substance.
- Kokoro real-time factor "under 1.0, low confidence" (section 7.1): map 05
  section 2. Correctly flagged.

## Minimal viable: ideas worth grafting

1. M0 toolchain spike before any corpus work, with measured render seconds
   per second and Kokoro real-time factor recorded in the framework.
2. Audio muxed by section offsets after render; sections rendered silent.
3. `look.py` as shipped code: `TexTemplate` packages, font default,
   `PURE_YELLOW`, role color constants.
4. Helpers imported rather than recalled, with `check_scenes.py` as the GL
   name gate.
5. The `verify.py` proxy for "visual changes when the subject changes".
6. The single `lesson.json` contract with single-writer fields.

## Ranking

The three totals are within one point (minimal viable 51, corpus fidelity
50, repeatable process 50), so the sum does not separate them. This lens is
asked to judge fidelity and whether the framework transfers, and on those
two criteria corpus fidelity leads by three and six points respectively.
Ranking under this lens:

1. Corpus fidelity. Its framework representation (two-check rules, tagged
   records, pattern pages with evidence and gotchas, discrimination tests,
   census) is the one that would actually encode what the corpus does. Its
   scope should be cut to the minimal viable phasing, not its method.
2. Minimal viable. The right order of operations (spike, runtime, then
   corpus) and the right shipping shape (helpers plus one contract), but a
   framework that is thin where it matters most, on narration, and a rubric
   with one corpus-contradicting item.
3. Repeatable process. The best gates and the best storyboard schema, but
   its two fidelity cuts (no camera, no intra-beat waits) remove devices the
   corpus uses constantly, and its per-section analysts cannot see the
   cross-section moves.

## What none of them handles

1. Rubric calibration against the corpus. All three test whether an agent
   given the framework scores well. None tests whether the rubric scores
   the corpus well: paraphrased storyboards of real 3b1b sections (which the
   analyses already contain) should score near the maximum, and any 3b1b
   section that scores low is evidence the rubric is wrong. Without this the
   rubric encodes the designers' taste, not his.
2. Continuity across section boundaries. All three render one `Scene` per
   section and concatenate with ffmpeg. Every section starts from a blank
   frame, so the network that stays at the bottom for ten minutes (map 01
   section 4, `to_edge(DOWN)` 26 uses) or the pipeline that stays on screen
   (map 02 section 8 move 10) becomes a jump cut at each boundary unless the
   next scene rebuilds the previous end state exactly. None of the designs
   has a rule, a helper (carry-over state from the previous section's final
   mobjects) or a check (perceptual distance between the last frame of
   section N and the first frame of N+1).
3. Motion review. Every frame reviewer looks at two or three stills per
   beat. The 3b1b look is in the motion: easing, travel arcs, stagger,
   nothing teleporting. A contact sheet of six to eight evenly spaced frames
   per beat, or a short low-fps strip, costs almost nothing and is the
   minimum a reviewer needs to see a transform rather than its endpoints.
4. Lead and lag between word and visual. Every sync gate is symmetric
   ("within 0.5 s"). 3b1b usually shows the thing slightly before naming it
   or lands the transform on the noun; "name then show" reads as lecture
   slides. Corpus fidelity collects the signal and none of the three turns
   it into a signed storyboard field and a check.
5. Narration prose voice. The license rule (no verbatim runs over 12 or 13
   words) is right, but it means no design can quote the narration it is
   trying to learn from, and none states how narration-voice rules (second
   person, planted questions, hedges, sentence length per beat) will be
   derived or checked under that constraint. The transcript analyses will
   produce paraphrase, and paraphrase does not carry voice.
6. The encode-time look. 3b1b's finished videos pass through a 1.5x
   saturation filter at encode (map 03 section 1.1), so his on-screen
   colors are 50 percent more saturated than the constants every design
   copies. None of the three mentions it; `assemble.py` should offer the
   equivalent `eq=saturation` option or the color contract will look flat
   next to the reference.
7. Between-beat prosody and pauses. Per-beat synthesis produces one
   utterance per beat with no breath or pitch continuity. Only corpus
   fidelity mentions ElevenLabs continuity fields; none states the pause
   length between beats or how Kokoro's per-beat output is joined without
   an audible reset.
