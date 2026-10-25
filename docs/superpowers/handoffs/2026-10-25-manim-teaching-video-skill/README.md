# Handoff: Manim teaching-video skill (design in progress)

Status: brainstorming, architectural path, between step 4 (approaches proposed) and
step 5 (owner approves the design). Nothing has been implemented. This folder is
session scaffolding for the hand-off between two cloud sessions; delete it once the
spec and plan land, or keep `maps/` as research input for the analysis phase.

## Resume prompt

Paste this as the first message of the new session (after checking the environment
checklist below):

```text
Resume an in-progress design for a new skill in this .agents kit. First run:
  git fetch origin claude/relaxed-faraday-x71bqk && git merge --ff-only origin/claude/relaxed-faraday-x71bqk
then read docs/superpowers/handoffs/2026-10-25-manim-teaching-video-skill/README.md and
docs/superpowers/handoffs/2026-10-25-manim-teaching-video-skill/design-proposal.md in full.

We are mid-way through the superpowers:brainstorming skill on the ARCHITECTURAL path. Load that
skill and resume at step 5: present the design proposal to me section by section for approval.
Do not restart from step 1 and do not re-ask the decisions recorded in the README. Ultracode is
on for this work: run substantive phases as Workflow orchestrations.

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
   `cdn-lfs.huggingface.co`, with the package-managers box ticked. Hugging Face hosts
   the Whisper and local text-to-speech model downloads.
2. Verify before any network-dependent work:

   ```bash
   for u in https://www.youtube.com/ https://www.3blue1brown.com/ https://docs.manim.community/ https://huggingface.co/; do
       curl -sS -o /dev/null -w "%{http_code} $u\n" --max-time 15 "$u"
   done
   ```

   A `000` or `403` means the host is still blocked: stop and report it.

## Contents of this folder

- `design-proposal.md`: the synthesized design, awaiting owner approval. Read first.
- `critique.md`: the adversarial completeness check applied to the proposal; the
  proposal's final "Revision notes" section lists what changed in response.
- `maps/`: evidence maps written by parallel readers. Reusable as research input for
  the corpus analysis phase.
- `design-process/architectures/`: the three candidate architectures (corpus-fidelity,
  repeatable-process, minimal-viable).
- `design-process/judgments/`: three judges' scorecards with distinct lenses.

## Process position and next steps

Brainstorming checklist (architectural path):

1. Explore project context: done.
2. Visual companion: not needed.
3. Clarifying questions: done (output scope answered: finished narrated video).
4. Propose approaches: done, in `design-proposal.md`.
5. Present design, get approval: next. Present section by section; stop for an
   explicit yes.
6. Write the spec to `docs/superpowers/specs/2026-10-25-manim-teaching-video-skill-design.md`
   and commit.
7. Spec self-review (placeholders, consistency, scope, ambiguity).
8. Owner reviews the spec.
9. Invoke `superpowers:writing-plans`; the owner selects the execution method.
