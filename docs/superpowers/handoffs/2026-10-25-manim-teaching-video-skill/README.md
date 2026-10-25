# Handoff: Manim teaching-video skill (design in progress)

Status: brainstorming, architectural path, between step 4 (approaches proposed) and
step 5 (owner approves the design). Nothing has been implemented. This folder is
session scaffolding for the hand-off between two cloud sessions. The design
proposal suggests `docs/research/manim-teaching-video/` as the lasting home for
the maps, architectures, judgments and proposal; move them there when the spec
lands and delete the rest of this folder.

## Resume prompt

Paste this as the first message of the new session (after checking the environment
checklist below):

```text
Resume an in-progress design for a new skill in this .agents kit. First run:
  git fetch origin claude/relaxed-faraday-x71bqk && git merge --ff-only origin/claude/relaxed-faraday-x71bqk
then read docs/superpowers/handoffs/2026-10-25-manim-teaching-video-skill/README.md and
docs/superpowers/handoffs/2026-10-25-manim-teaching-video-skill/design-proposal.md and
docs/superpowers/handoffs/2026-10-25-manim-teaching-video-skill/decision-briefing.md in full.

We are mid-way through the superpowers:brainstorming skill on the ARCHITECTURAL path. Load that
skill and resume at step 5: present the design proposal to me section by section for approval,
and collect my answers to its nine "Decisions needed from the owner" (the README lists them
with any answers I have already given). Do not restart from step 1 and do not re-ask the
decisions recorded in the README. Ultracode is on for this work: run substantive phases as
Workflow orchestrations.

After I approve the design: write the spec to
docs/superpowers/specs/2026-10-25-manim-teaching-video-skill-design.md, self-review it, commit,
and ask me to review it. Only after I approve the spec, invoke superpowers:writing-plans.
Work in a git worktree under ~/worktrees/ per the kit's rules.
```

## Goal

A skill in this kit that, given a topic, reliably produces a 3Blue1Brown-grade
narrated teaching video using Manim Community Edition (ManimCE). One run produces a
finished video: script, synthesized narration, Manim animation synced to the
narration, rendered MP4. Success means the videos look and teach like 3Blue1Brown's,
not merely render.

Agreed path:

1. Build a corpus from the 3Blue1Brown neural-network series.
2. Analyze each video into a structured record of what he does and why it works.
3. Synthesize a framework: rules, a ManimCE pattern library, a quality rubric.
4. Build the skill with `superpowers:writing-skills` as the spine (TDD for skills:
   baseline a subagent without the skill, watch it fail, write the skill, re-test),
   `skill-creator`'s eval scripts for a fixed test-prompt set re-run after each edit,
   and `deep-research` for the synthesis step alongside the corpus.

## Decisions already made (do not re-ask)

- Output of one run is a finished narrated video, not scenes or a script alone.
- Target ManimCE, not 3b1b's ManimGL. The 3b1b source is ManimGL; the framework
  translates idioms.
- Primary corpus is the public 3b1b Manim source plus transcripts, aligned per video
  section. Downloaded video keyframes are a secondary check.
- We write the YouTube download, transcript and keyframe tooling ourselves; no
  third-party plugin.
- The finished skill bundles everything it needs: framework, pattern library, rubric,
  per-video analyses, scripts. It never depends on chat history or files outside the
  skill.
- Narration provider is pluggable, with a stated default (see the design proposal's
  assumptions).
- License: `3b1b/videos` is CC BY-NC-SA 4.0. Derive principles, write original ManimCE
  examples, never copy his scene code into the skill.
- Follow the kit's rules in `agents.md`: worktrees, look-it-up, minimal changes,
  delegate to subagents.

## Facts found in the first session

Corpus source:

- Clone with `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/3b1b/videos /home/user/3b1b/videos`
  (call `add_repo 3b1b/videos` first; it answers that anonymous read is available).
- Series code: `_2017/nn/part1.py`, `part2.py`, `part3.py` (chapters 1-4, about 13k
  lines) and `_2024/transformers/` (embedding, attention, mlp, network_flow,
  generation, ml_basics, chm, auto_regression, supplements, helpers; about 22k lines).
  Shared infrastructure: `custom/` (backdrops, characters, drawings, end_screen, logo,
  opening_quote), `manim_imports_ext.py`, `custom_config.yml`, `stage_scenes.py`. Also
  `_2026/cross_entropy/transformer_render.py`.

Kit constraints:

- Skills live at `skills/<id>/SKILL.md` with frontmatter keys `description`,
  `enabled`, `id`, `name` (sorted, `id` equals the directory name), checked by
  `scripts/validate.sh`.
- `scripts/install.sh` copies only `*.md` files from skill directories, so bundling
  scripts needs a deliberate change there and in the CI install smoke test.
- CI gates on every file: markdownlint, typos, lychee (every URL must resolve),
  gitleaks, jscpd, shellcheck, shfmt, yamllint, actionlint. README skills table and
  CHANGELOG must be updated when a skill ships. ADRs live in `docs/adr/`.

Container of the first session:

- ffmpeg present; manim, yt-dlp, whisper and LaTeX not installed; PyPI reachable;
  4 CPUs, 15 GB RAM.
- youtube.com, googlevideo.com, ytimg.com, 3blue1brown.com, docs.manim.community and
  3b1b.github.io were blocked by the environment's network policy. The owner changed
  the policy, but the change did not reach the running session, hence this hand-off.

## Environment checklist for the new session

1. Use the edited environment. Either a broader network access level or an allowlist
   with at least: `www.youtube.com`, `youtube.com`, `*.googlevideo.com`,
   `i.ytimg.com`, `www.3blue1brown.com`, `docs.manim.community`, `3b1b.github.io`,
   `github.com`, `raw.githubusercontent.com`, `huggingface.co`,
   `cdn-lfs.huggingface.co`, `storage.googleapis.com`, with the package-managers box
   ticked. Hugging Face hosts the Whisper and local text-to-speech model downloads;
   the Google storage bucket hosts the 3blue1brown.com lesson figures the corpus
   pipeline fetches.
2. Verify before any network-dependent work:

   ```bash
   for u in https://www.youtube.com/ https://www.3blue1brown.com/ https://docs.manim.community/ https://huggingface.co/; do
       curl -sS -o /dev/null -w "%{http_code} $u\n" --max-time 15 "$u"
   done
   ```

   A `000` or `403` means the host is still blocked: stop and report it.

3. Add the system packages to the environment's setup script (cloud environment
   menu in the title bar, then Edit; the script runs at the start of every new
   session, one directory above the repository). ManimCE's `manimpango`
   dependency has no Linux wheel and compiles against the Pango headers, and
   formulas need a TeX distribution. The design session could not install
   either because its container had no package-mirror access:

   ```bash
   apt-get update && apt-get install -y build-essential pkg-config libcairo2-dev libpango1.0-dev ffmpeg \
       texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-science dvisvgm
   ```

   Kokoro's phonemizer falls back to `espeak-ng` for unknown words; add it if
   M0 confirms the need. Use Python 3.11 or 3.12 for the Manim virtualenv
   (`uv venv --python 3.12`); the Kokoro wheel declares Python below 3.13.

## Design summary (from `design-proposal.md`)

Three architectures were drafted from different angles and scored by three
judges with distinct lenses; their totals landed within five points of each
other, and all three judgments named the same hybrid. The recommendation is a
**spike-first gated pipeline with an evidence-grounded framework**:

- From the minimal-viable design: a toolchain spike (M0) before any corpus
  work, then a hand-written lesson rendered to a verified MP4 with no model in
  the loop (M1), then the corpus (M2), then skill TDD (M3). One `lesson.json`
  contract with a single writer per field; a small shipped `mtv` package with
  narrated scene base classes, the house look and imported pattern helpers so
  generated scenes import idioms rather than recall them; silent renders with
  narration muxed by beat offset, so a voice change re-renders nothing.
- From the repeatable-process design: input hashes and resume at the first
  changed stage, bounded loops with named escalations, one `manim` process per
  scene run concurrently, a self-test that runs without ManimCE, frames
  extracted at mark times, a sync gate backed by a run log the scene writes
  itself, and a pass definition that requires the no-skill baseline to fail.
- From the corpus-fidelity design: rules in a fixed form (`Statement`, `Why`,
  `Apply`, `Check (storyboard)`, `Check (code or frames)`, `Scope`, `Fails`),
  per-section analysis records with `file:line` and timestamp citations
  enforced by a citation checker, a refuter and a census.

Narration defaults to Kokoro-82M offline with ElevenLabs as the premium option;
manim-voiceover is not a dependency. Release corpus is two videos (chapter 1 of
2017 and the attention chapter of 2024), the other six as an extension loop.
The adversarial critique found no blocker, ten major gaps and twenty-two minor
ones; the proposal's "Revision notes" section records how each was resolved.

### Decisions the proposal needs from the owner

The proposal's recommendation is in parentheses. Answers given so far are
recorded here; the rest are collected at step 5.

1. Corpus tooling location: separate MIT repository `manim-3b1b-corpus`
   (recommended) versus a `tools/` directory inside the kit.
2. Media policy at release: captions plus the site's figure bucket only
   (recommended) versus downloading the eight videos for keyframes.
3. Agents: five inlined role prompts in `references/roles.md` (recommended)
   versus five new entries under `agents/`.
4. Math engine: LaTeX as a hard preflight requirement (recommended) versus a
   Typst or text-only fallback mode.
5. Corpus depth at release: two videos (recommended) versus all eight before
   the skill ships.
6. Whether a 2160p `final` tier is in scope for v1, or `standard` 1080p is the
   ceiling until render times are measured.
7. Whether to reopen ADR-0002 and add a Python test step to CI for the bundled
   scripts, or keep `selftest.py` manual (recommended).
8. License granularity of the analyses: analyses stay in the corpus
   repository under CC BY-NC-SA and the kit ships only the framework, pattern
   index and rubric (recommended), or the analyses ship inside the skill with
   an ADR explaining why.
9. Description style: the kit's own style (capability plus trigger phrases,
   no workflow summary) rather than the writing-skills "triggers only" rule;
   a conscious deviation the owner should confirm.

## Contents of this folder

- `design-proposal.md`: the synthesized design, awaiting owner approval. Read first.
- `decision-briefing.md`: background the owner asked for on each of the nine
  decisions (sizes, storage, inlined roles versus agents, what LaTeX entails,
  corpus depth, render-time expectations, ADR-0002, license, description style).
- `critique.md`: the adversarial completeness check applied to the proposal; the
  proposal's final "Revision notes" section lists what changed in response.
- `maps/`: evidence maps written by parallel readers. Reusable as research input for
  the corpus analysis phase. Already lint-clean under the kit's gates: table
  delimiter rows are spaced for markdownlint's table-style rule, and the four
  misspelled identifiers the maps quote from the 3b1b source are listed in the
  root `.typos.toml`, so the proposal's "research hygiene" step for the maps is
  done.
- `manim-skill-design.js`: the Workflow script that produced everything here, kept
  so the process can be re-run or audited.
- `design-process/architectures/`: the three candidate architectures (corpus-fidelity,
  repeatable-process, minimal-viable).
- `design-process/judgments/`: three judges' scorecards with distinct lenses.

## Process position and next steps

Brainstorming checklist (architectural path):

1. Explore project context: done.
2. Visual companion: not needed.
3. Clarifying questions: done (output scope answered: finished narrated video).
4. Propose approaches: done, in `design-proposal.md` (three approaches, a recommended hybrid).
5. Present design, get approval: next. Present section by section; stop for an
   explicit yes.
6. Write the spec to `docs/superpowers/specs/2026-10-25-manim-teaching-video-skill-design.md`
   and commit.
7. Spec self-review (placeholders, consistency, scope, ambiguity).
8. Owner reviews the spec.
9. Invoke `superpowers:writing-plans`; the owner selects the execution method.
