# Judgment: agent reliability and skill authoring

Lens: would an agent following each candidate skill behave consistently? I
judged context budget and progressive disclosure, failure modes, whether the
verification loops catch bad output or only confirm their own inputs,
ambiguity an agent would trip on, compliance with the writing-skills and
skill-creator methods, and how testable the skill itself is.

Inputs read in full: the three architectures under `architectures/`
(`corpus-fidelity.md`, 813 lines; `repeatable-process.md`, 892 lines;
`minimal-viable.md`, 751 lines). Feasibility checks were made against the
seven maps under `maps/` (cited as `map NN:line`), the kit rules
(`rules/subagents.md`), the installed writing-skills and skill-creator
`SKILL.md` files, the local ManimCE 0.22.0 clone and `_2017/nn/part1.py`.
Claims I could not check are marked unverified.

## Scoring method

Seven criteria, each 1 to 10, one sentence per score, then a total out of 70.
Scores are relative to the three candidates and to this lens; a design that is
excellent on fidelity but hands the agent an unbounded loop loses points here
even if another judge would reward it.

## Candidate A: corpus-fidelity

File: `architectures/corpus-fidelity.md`.

### Corpus-fidelity scores

| # | Criterion | Score | Justification |
| --- | --- | --- | --- |
| 1 | Output-quality fidelity | 9 | Twenty-four principles each with an apply rule and two checks (lines 354-382), 44 patterns rendered in CI (lines 384-406) and a 20-item rubric with gate items (lines 408-422) give the agent the most complete, checkable account of what 3b1b does. |
| 2 | Repeatability | 6 | Corpus steps are idempotent via `.done.json` sidecars (lines 129-133) and narration is cached by hash (line 492), but the run-time pipeline has no state record at all, so an interrupted run has no defined resume point. |
| 3 | Feasibility | 5 | Nineteen focused sessions (line 744), three analyst roles plus two verifier roles per video plus inter-analyst agreement (lines 193-329), 44 pattern reference frames compared by perceptual hash (lines 641-644) and about four hours of user anchor time (line 798) make this the heaviest plan by a wide margin. |
| 4 | Corpus leverage and evidence grounding | 10 | `cite_check.py` (lines 281-297), a refuter pass, a census comparing tag histograms with the grep counts in maps 01 and 02 (lines 317-323) and a 13-word verbatim guard (line 292) make it near impossible for an analysis to drift from evidence. |
| 5 | Kit and skill-authoring fit | 7 | The load-order table (lines 428-433), `SKILL.md` under 200 lines, evals written before `SKILL.md` and RED first (lines 673-678) follow the method; five new `mv-*` agents, two ADRs, nine open decisions and a description that lists outputs (lines 447-451) cut against it. |
| 6 | Testability | 8 | The rule discrimination test (lines 651-654), the framework-only generation test (lines 645-650), per-script fixtures and a pass bar that requires beating the baseline on every objective grader (line 684) are strong; pattern CI by perceptual hash will be brittle across Cairo and font versions. |
| 7 | Simplicity and YAGNI | 3 | Forty-four patterns, 24 principles, 20 rubric items, 13 run-time scripts, eight analysis files, five agents and a six-signal alignment DP are far more surface than the first good video needs; the thin slice (M1 and M2) acknowledges this but does not cut it. |

Total: 48 of 70.

### Corpus-fidelity strengths

- The only design whose rules are written as a contract an agent can both
  apply and verify: `Apply`, `Check (storyboard)` and `Check (code)` per
  principle, with the static part implemented in `lint_scene.py` (lines
  360-382).
- Progressive disclosure is explicit: a load-order table names which
  references each stage reads, `patterns/INDEX.md` is the only file that
  lists everything, and per-pattern files are fetched by id, with token
  budgets stated (lines 426-438).
- Error handling is a table of failure, detection and response with bounded
  retries and escalation (lines 559-569); the LaTeX-missing branch names the
  exact substitution (`Text` labels, `MathTypst` formulas), which map
  04:148 and 04:387 confirm exist in CE 0.22.0.
- The skill test set spans five topics across and beyond the corpus domain
  plus three pressure scenarios phrased as writing-skills discipline tests
  (lines 658-671).
- The tier table with budget targets and the "ask before the final render"
  rule (lines 571-586) keep the agent from spending hours unattended.

### Corpus-fidelity weaknesses

- No run-time resume. Section 6.4 defines three loops but nothing records
  which gate passed; after a usage-limit cutoff (the very event that
  triggered this workflow) the agent must infer state from the output
  directory. Narration and ManimCE caches reduce rework but do not define
  where to restart.
- Hundreds of subagent dispatches in M3 (three roles per section, 8 to 14
  sections per video, eight videos, plus refuters, census critics and
  duplicate analyses), each returning JSON the parent must write to disk
  (line 214). Any malformed return or vocabulary drift stalls the census;
  the design has no handling for a subagent that returns non-conforming
  JSON.
- The frame reviewer scores "motion direction matches meaning" and
  "dim-not-delete when focus shifts" (line 416) from stills; motion is not
  observable in a still, so those items will be guessed.
- The rubric pass bar (every gate at 2, 34 of 40, no zeros; line 420) is
  strict for a 20-item LLM judgment; the design has no two-judge or
  calibration mechanism, so flaky fails at the storyboard gate are likely.
- `add_sound` is called inside cached scenes "so the section MP4s have audio
  for the frame reviewer" (lines 620-622) while the reviewer actually reads
  PNGs; manim-voiceover requires `--disable_caching` for an unstated Manim
  bug (map 05:63 and 05:164), so the interaction is a risk taken for no
  benefit.
- Human anchors (30 minutes per video, lines 327-329 and 798-800) place a
  manual step in the middle of an otherwise automated corpus phase; if the
  user is absent the census blocks.
- The storyboard YAML (lines 512-528) carries `bookmarks: {reveal: "network that"}`
  as a substring; the design does not say how a bookmark is resolved when the
  phrase repeats or when Kokoro's tokens split it differently.

### Corpus-fidelity factual errors and unverified claims

- `IntroduceWeights` is cited as lines 2237-2617 (line 233); map 01:111
  confirms the start at 2237 but gives no end line (the next class,
  `IncludeBias`, starts at 2780 per map 01:114). The end line is unverified.
- The proposed `AGENT_REF` replacement `(?:cr|mv)-[a-z][a-z-]*` (line 719)
  would drop the `researcher-lite|mid|deep` alternatives the current regex
  also validates (map 06:594). It must be an added alternative, not a
  replacement. Repeatable-process repeats the same wording.
- The claim that section MP4s with audio help the frame reviewer (line 621)
  is unsupported by the design itself, which feeds the reviewer PNGs (line
  495).
- Kokoro on Python 3.13 via GitHub and `kokoro-onnx` token timestamps are
  correctly marked unverified (line 594), matching map 05:204 and 05:745.
- Whisper timing ("roughly real time or slower", line 184) is an
  extrapolation the map itself rates low confidence (map 07:474).

### Corpus-fidelity ideas worth grafting

1. The `Apply` / `Check (storyboard)` / `Check (code)` rule format with the
   static checks implemented in a lint script.
2. The load-order table in `SKILL.md` plus an index-only pattern lookup.
3. The rule discrimination micro-test: one compliant and one violating
   storyboard snippet per rule, graded with the rule text; rewrite rules that
   do not separate them.
4. `cite_check.py` with the 13-word verbatim guard and the census comparing
   technique-tag histograms with grep counts, scaled down to whatever corpus
   depth the synthesis adopts.
5. The explicit tier table with a "measure at `-ql`, estimate, ask before the
   final render" rule.

## Candidate B: repeatable-process

File: `architectures/repeatable-process.md`.

### Repeatable-process scores

| # | Criterion | Score | Justification |
| --- | --- | --- | --- |
| 1 | Output-quality fidelity | 7 | About 30 rules with apply, check, why and fails (lines 270-299), 24 patterns and an 18-item rubric cover the 2017 regime well, but cutting all 3D and camera orbits from v1 (lines 835-838) removes the signature of the 2024 videos. |
| 2 | Repeatability | 9 | `state.json` with input hashes and tool versions, resume at the first stage whose inputs changed (lines 396-403), one `manim` process per scene (line 556), a bounded-loop table with escalation (lines 536-549) and a defined meaning of "stop" make this the most deterministic run-time design. |
| 3 | Feasibility | 7 | Nineteen to twenty-four days is moderate, but the static run-time-sum check (line 670) cannot see non-literal values, the one-frame drift tolerance (lines 486-488) is tight against frame-quantized waits, and the ban on `wait()` inside beats contradicts the pacing rules. |
| 4 | Corpus leverage and evidence grounding | 7 | Per-section analysts with the alignment handed to them (lines 170-184), a refuter, cross-video vocabulary convergence and a coverage rule (lines 236-250) are solid, but the analyses are never loaded at run time (line 267), so corpus depth reaches the agent only through the framework. |
| 5 | Kit and skill-authoring fit | 8 | A 1,500-word orchestrator, named files per agent (lines 259-268), a pass definition that requires the baseline to fail (line 733), vocabulary added to `CONTEXT.md` and a description re-check against the kit contract (line 736) follow the method closely; five new agents and a description that lists outputs are the cost. |
| 6 | Testability | 8 | `selftest.py` runs without ManimCE using a `null` TTS provider and synthetic clips, `--one-beat` finishes in under two minutes (lines 679-687), a fixture with a known off-screen label is caught (line 88), and six prompts including a non-math one (lines 708-719); no run-count or variance policy. |
| 7 | Simplicity and YAGNI | 6 | Eleven scripts, five provider modules, five agents and 24 patterns are proportionate to the gate design; the storyboard schema (lines 499-534) adds four bookkeeping fields per beat that every stage must honor. |

Total: 52 of 70.

### Repeatable-process strengths

- The storyboard schema is the single contract and `scripts/common.py` is its
  only parser (lines 530-534), so stages cannot disagree about the format.
- Narration-first timing: the beat's audio length is its duration budget and
  the runtime pads the rest (lines 666-673), which turns sync from a judgment
  into arithmetic.
- Frames are extracted at bookmark times and the reviewer is asked a single
  observable question per frame, "is the thing the narration names on screen
  and legible" (lines 467-474). This is the only design whose visual check
  looks where the sync matters.
- The runtime writes a bounding-box log at the end of each beat (lines
  469-470), so clipping is caught by code rather than by vision.
- Render errors are regex-matched against the map 04 error table and the
  matching fix text is fed into the coder's retry prompt (lines 553-557);
  a hung render is killed after ten silent minutes and retried once (lines
  574-576).
- The LaTeX decision is made at G0 before any content exists, with a
  `text_only` engine that forbids the exact classes map 04:385 lists (lines
  558-565).
- The pass definition for the skill requires the baseline to fail at least
  one objective grader on four of six prompts (line 733), which is the
  skill-creator's non-discriminating-assertion check applied up front.

### Repeatable-process weaknesses

- Internal contradiction: `check.py` rejects "hard-coded `wait()` inside a
  beat (the runtime pads)" (lines 457-458) while the pacing rules demand "1 s
  wait after most plays, 2 s wait closing a step" (lines 294-296). An agent
  following both will fail the static gate or break the rhythm; the design
  needs `until()` or an explicit intra-beat pause idiom.
- The static check that "declared `run_time`s sum to more than the audio
  length minus 0.3 s" (lines 670-672) is only decidable for literal
  `run_time` values; `until()`-derived values defeat it, so the gate gives
  false confidence.
- Vocabulary collision: the design's "section" is a storyboard section (one
  `Scene`) while ManimCE's "section" is one `next_section` call (one beat).
  "placing each beat WAV at its section start" (line 483) and "per-section
  drift" (line 488) are ambiguous as written; an agent could place all beat
  WAVs of a scene at the scene start.
- The one-frame drift tolerance (lines 486-488 and 673) assumes `wait()`
  renders exactly `duration * fps` frames; frame quantization across several
  beats can exceed one frame. Unverified against `scene.py:1242`, but the
  design does not say how the runtime compensates.
- `beat()` calls `add_sound(wav)` (line 650) with caching left on (line
  466); manim-voiceover documents `--disable_caching` as required for a Manim
  bug (map 05:63 and 05:164). Whether `add_sound` is the trigger is
  unverified, but the design takes the risk silently.
- The rubric's V group includes "motion direction matches data flow" (line
  343), scored from frames, which cannot show motion.
- No statement of how many runs per eval case or how variance is handled,
  although skill-creator supports `run-N` directories and reports mean and
  standard deviation.

### Repeatable-process factual errors and unverified claims

- The example analysis record cites `part1.py:1047-1053` as evidence for a
  `staggered_reveal` idiom (line 205). Those lines are the step-method list
  of `IntroduceEachLayer.construct` (verified in the clone; map 01:361 says
  the same). The design's own `check_analysis.py` rule, that the cited lines
  must contain the idiom token, would reject this example, which shows the
  check works and the example is wrong.
- The `AGENT_REF` change (line 780) has the same replacement-versus-addition
  problem noted for corpus-fidelity.
- Render budget constants (draft 5 minutes, standard 40, uhd 3 hours; lines
  571-574) are correctly labeled unverified calibration targets.
- The claim that the manim-voiceover lock file resolves to ManimCE 0.20.1
  (line 661) matches map 05:169 and 05:176.
- Piper "GPL used as a subprocess" (line 610) matches map 05:263-265.

### Repeatable-process ideas worth grafting

1. `state.json` with input hashes, resume at the first changed stage, and the
   defined meaning of "stop" (write the report, keep artifacts, say how to
   resume).
2. Frames at bookmark times with the one-question frame review, plus the
   runtime bounding-box log as a code check.
3. `selftest.py` that runs without ManimCE via a `null` provider and
   synthetic media, and a `--one-beat` end-to-end smoke under two minutes.
4. The pass definition that requires the baseline to fail (discriminative
   evals).
5. Regex-matching render errors to the map 04 table and injecting the fix
   row into the retry prompt; one `manim` process per scene; kill-and-retry
   on a silent log.
6. Deciding the math engine at preflight with a `text_only` mode that
   forbids the LaTeX-dependent classes by name.

## Candidate C: minimal-viable

File: `architectures/minimal-viable.md`.

### Minimal-viable scores

| # | Criterion | Score | Justification |
| --- | --- | --- | --- |
| 1 | Output-quality fidelity | 6 | The framework is seeded from maps 01 to 05 and two analyzed videos, ten imported helpers encode the key moves (lines 309-324) and the rubric has 12 criteria; the sync gate is satisfied by construction, so visual-on-word landing is checked only by two frames per beat. |
| 2 | Repeatability | 7 | `lesson.json` with one writer per field (lines 129-132) makes resume well defined, but there are no input hashes, so a stage cannot tell its inputs changed; loops are bounded (one storyboard retry, two fix passes). |
| 3 | Feasibility | 8 | M0 is a hand-written toolchain spike before any corpus work (lines 22-27 and 676), nine to ten days to first release, no new agents and three single-expression kit changes; two command-line and verification claims are wrong (below). |
| 4 | Corpus leverage and evidence grounding | 5 | Two videos, bucket figures as the keyframe stand-in, a ten-claim refuter and an exact-line copied-code guard (lines 251-259) are honest but shallow; alignment "refines rules rather than gating them" (line 692). |
| 5 | Kit and skill-authoring fit | 8 | Inlined role prompts in `references/roles.md` use the kit's generic-fallback rule (`rules/subagents.md:25`) and avoid the `AGENT_REF` change; the kit diff is the smallest; but the parent "checks the narrative rules by reading, not by subagent" (lines 418-419), which the kit's delegation rule discourages, and `roles.md` is validated by no gate. |
| 6 | Testability | 6 | pytest per unit boundary (lines 562-580) and a framework test before the skill exists are good, but three in-domain topics (lines 616-623) with a "two of three" pass bar is a noisy signal, there is no off-domain prompt until M4, and the sync grader passes by construction. |
| 7 | Simplicity and YAGNI | 9 | One contract, six scripts, a small `mtv` package, ten helpers, 12 criteria and a cut table that names how each cut comes back (lines 699-715). |

Total: 49 of 70.

### Minimal-viable strengths

- The toolchain spike comes first (M0), on the correct observation that
  nothing in the render, TTS or sync chain has been executed and a wrong
  assumption there invalidates everything downstream (lines 22-27).
- `lesson.json` is written by exactly one stage per field (lines 129-132),
  which makes "rerun the stage whose outputs are missing" an unambiguous
  rule.
- Audio is never added inside Manim; sections render silent and
  `assemble.py` places WAVs by section offsets (lines 544-547), so ManimCE
  caching stays valid, voice changes never re-render a frame, and the
  manim-voiceover caching bug is avoided entirely.
- Pattern helpers are imported from `scripts/mtv/patterns.py` rather than
  recalled from training data (line 691), which directly attacks the
  highest-likelihood failure in all three risk tables (ManimGL idioms).
- `preflight.py` measures Kokoro real-time factor on a ten-word sentence and
  records it (line 514), turning a low-confidence map figure into a measured
  constant at the start of every run.
- The `until(word)` fallback to proportional interpolation is recorded in
  the report (lines 528-531), so a degraded timing path is visible.

### Minimal-viable weaknesses

- The sync gate is tautological: audio is placed at section offsets computed
  from the same JSON index that `verify.py` then compares against (lines
  471-474). It can only detect an animation overrun, which `NarratedScene`
  already warns about. Nothing checks that the named visual is on screen at
  the named word; frames are taken at mid and end of the beat, not at
  bookmark times (lines 444-447).
- Rubric criterion 8, "1 to 3 plays per narration sentence, no hold over 4 s
  without motion", is assigned to `verify.py` "from section JSON" (line 344).
  The section index holds name, type, video, codec, dimensions, frame rate,
  duration and frame count per section (map 04:296); it carries no play
  count and no motion information, so the check is not computable from the
  stated input.
- Criterion 12 cites "`verify.py` bounding boxes" (line 348), but no
  component writes bounding boxes: `NarratedScene` (lines 535-542) logs only
  overruns and `verify.py` reads the MP4 and `lesson.json`.
- `self.play(..., run_time=b.until("digits"))` (line 433) raises
  `ValueError` when the word has already passed, because CE rejects
  `run_time <= 0` (map 04:121); the design does not clamp.
- The parent performs rubric work itself ("hook present, plan previewed,
  hedges present", line 419), adding judgment variance and context load to
  the orchestrator.
- Three in-domain test topics make over-fitting to the corpus invisible
  until M4; the pass bar "two of three on first try" cannot distinguish a
  good skill from a lucky run.
- `references/roles.md` holds five agent definitions outside `agents/`, so
  none of the agent frontmatter checks apply and nothing stops a role prompt
  from drifting away from the kit's agent contract.

### Minimal-viable factual errors and unverified claims

- `--disable_caching_warning` is used as a CLI flag (line 443). In the CE
  0.22.0 clone the CLI defines only `--disable_caching`
  (`manim/cli/render/global_options.py:65`); `disable_caching_warning` is a
  `manim.cfg` key (`manim/_config/default.cfg:134`, map 04:372). The flag
  as written would fail.
- `-ql --fps 15` is redundant (`-ql` already selects 15 fps, map 04:342) but
  harmless; `--fps` exists (`render_options.py:206-207`).
- The rubric criterion 8 and criterion 12 mechanisms are not supported by
  the artifacts named (above).
- The Typst fallback is marked unverified (line 729); map 04:148 and 04:387
  verify `Typst` and `MathTypst` exist in CE 0.22.0 behind `manim[typst]`,
  so this is over-cautious rather than wrong; whether it works on a consumer
  machine is still unverified.
- "The useful core is about 400 lines under MIT" (line 556) for
  manim-voiceover is a line count the maps do not give; unverified.
- The Kokoro real-time factor "under 1.0, low confidence" (line 513) matches
  map 05:245-248.

### Minimal-viable ideas worth grafting

1. M0 as a hand-written two-beat spike that measures render seconds per
   second and Kokoro real-time factor before any corpus or framework work.
2. One `lesson.json` contract with a single writer per field.
3. Silent section renders with audio muxed by section offset after render:
   cache stays valid and voice swaps never re-render.
4. An imported helper package (`mtv`) so idioms are imported, not recalled;
   bundle any helper two eval runs wrote independently (skill-creator
   heuristic).
5. Inlined roles in a reference file for v1, with promotion to `agents/`
   only when a second skill reuses them.
6. A "deliberately cut" table whose third column names how each cut comes
   back as a repeat of an existing step.

## Ranking

1. repeatable-process, 52 of 70. Under this lens it wins on the things an
   agent needs most: a state record with hashes, bounded loops with named
   escalation, a self-test that runs without the heavy toolchain, bookmark
   frame review, and a pass definition that proves the skill adds something.
   Its defects (the `wait()` contradiction, the non-decidable run-time sum,
   the section vocabulary collision) are each a paragraph to fix.
2. minimal-viable, 49 of 70. Best feasibility and simplicity, and the only
   design that avoids `add_sound` inside cached scenes and that spikes the
   toolchain first. It loses on verification that actually catches bad
   output: its sync gate and two of its rubric mechanisms do not measure what
   they claim.
3. corpus-fidelity, 48 of 70. Best framework and evidence discipline, and the
   best rule format, but as a skill an agent runs it has no run-time resume,
   the largest surface to keep consistent, and a corpus phase whose hundreds
   of subagent dispatches and human anchors are the most likely place for a
   long session to stall.

The totals are close because the designs are strong in different places; the
ranking reflects the lens, not an absolute verdict.

## Top ideas to graft into a synthesis

1. repeatable-process `state.json` with input hashes and resume at the first
   changed stage, combined with minimal-viable's single-writer-per-field
   `lesson.json` so the two mechanisms are one file.
2. Narration-first padding (`beat()` context manager) with minimal-viable's
   silent render plus post-render mux, and repeatable-process's bookmark-time
   frame extraction and runtime bounding-box log as the visual checks.
3. corpus-fidelity's rule format (`Apply`, `Check (storyboard)`,
   `Check (code)`) with the static checks in one lint script, and its rule
   discrimination micro-test for every rule.
4. repeatable-process's `selftest.py` with a `null` TTS provider and a
   `--one-beat` end-to-end smoke under two minutes, run before every commit.
5. minimal-viable's M0 spike as the first milestone of any plan, measuring
   render throughput and Kokoro real-time factor.
6. An imported pattern helper package rather than pattern example files to
   copy; keep corpus-fidelity's index-only lookup and load-order table for
   the markdown references.
7. repeatable-process's discriminative pass definition (baseline must fail)
   and corpus-fidelity's five-topic cross-domain prompt set, with a stated
   number of runs per case and the skill-creator variance report.
8. corpus-fidelity's `cite_check.py` and verbatim guard for whatever corpus
   depth is chosen; start at minimal-viable's two videos and extend by
   repeating the step.
9. repeatable-process's preflight-decided math engine with a `text_only`
   mode, and its regex-matched error table injected into retry prompts.
10. minimal-viable's inlined roles for v1 and its "how each cut comes back"
    table.

## What none of them handles

- The section vocabulary collision. All three use "section" for a storyboard
  unit rendered as one `Scene` and rely on ManimCE's `next_section`, whose
  output files and JSON index are also called sections. The synthesis should
  pick distinct words (for example "chapter" and "beat") and say which one
  the ManimCE index describes.
- Bookmark resolution. `until(word)` and `bookmarks: {name: "phrase"}` assume
  a word in the script maps to one token in the TTS timestamps. Kokoro
  returns tokens, numbers are verbalized ("784" becomes several words),
  punctuation splits differently, and a word may repeat in a beat. No design
  defines the normalization or the tie-break, and only corpus-fidelity
  mentions spelling out numbers, and only for forced alignment.
- Frame-quantized timing. Every drift gate (one frame, 0.25 s, 0.5 s)
  assumes `wait(remaining)` lands exactly; frames are integers, so the
  runtime must track the quantization error and the gate must be set with
  it in mind. Unverified in the CE source; none of the designs say.
- Rubric items about motion assigned to still-frame reviewers. Either the
  item moves to a code check (compare consecutive frames or inspect the
  animation list) or it is dropped from the frame reviewer.
- LLM judge calibration. Only repeatable-process proposes a second judge,
  and only at final tiers. None gives the critic anchor examples of a 0, a 1
  and a 2 per item, and none states how many runs per eval case count as a
  pass despite skill-creator reporting mean and standard deviation across
  runs.
- Eval wall-clock. A full eval at draft tier is a narration pass, a render
  and an assembly per prompt, with and without the skill, per iteration.
  Nobody budgets this or proposes a cheaper eval tier (for example storyboard
  and `--dry_run` only) for the inner loop.
- Description style. All three descriptions open with a capability sentence
  that lists the pipeline outputs. writing-skills forbids workflow summaries
  in descriptions because agents follow the summary instead of the body
  (writing-skills `SKILL.md:150-158`); the kit's own convention is
  capability plus triggers (map 06:120-121). Nobody resolves the tension or
  tests it with the `run_loop.py` near-miss set before release.
- Malformed subagent returns. Every design has the parent write files from
  subagent output, but none says what happens when a critic returns prose
  instead of the expected JSON or YAML, or when a scene coder returns code
  for the wrong section.
- `add_sound` versus caching. Two designs call `add_sound` in cached scenes;
  manim-voiceover requires `--disable_caching` for a bug the map does not
  identify (map 05:63 and 05:164). The M0 spike should test this
  explicitly, and the synthesis should default to the silent-render path.
- Orchestrator context across a long run. Only repeatable-process states
  that the parent holds "only the storyboard and the gate results"; none
  budgets the parent's context for a ten-stage run with several waves of
  subagents and multiple fix loops, or says when the parent should hand off
  to a fresh session with the state file.
