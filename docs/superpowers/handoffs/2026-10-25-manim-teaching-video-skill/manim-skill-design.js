export const meta = {
  name: 'manim-skill-design',
  description: 'Map the 3b1b corpus, ManimCE gap, tooling and kit constraints; then architect, judge, synthesize and critique a design for the Manim teaching-video skill',
  phases: [
    { title: 'Understand', detail: '7 parallel readers write structured maps' },
    { title: 'Design', detail: '3 architects from different angles' },
    { title: 'Judge', detail: '3 judges with distinct lenses score the architectures' },
    { title: 'Synthesize', detail: 'proposal, adversarial critique, revision' },
  ],
}

const OUT = '/tmp/claude-0/-home-user--agents/b713d8f3-7c52-540b-8252-65c41f426313/scratchpad/design'
const KIT = '/home/user/.agents'
const VIDEOS = '/home/user/3b1b/videos'
const WRITING_SKILLS = '/root/.claude/plugins/synced/cfde6f53-d88f-4bb9-921f-4a7e77b2d42a_f9827863-ee23-4d83-8085-4745e4fef36d/6ba53849-2ee0-4cf0-957e-31c122ea1dd1/skills/writing-skills'
const SKILL_CREATOR = '/root/.claude/skills/synced/cfde6f53-d88f-4bb9-921f-4a7e77b2d42a_f9827863-ee23-4d83-8085-4745e4fef36d/skill-creator'

const BRIEF = `
# Project brief (shared context; this is the only context you have)

We are designing a new skill for a personal agent kit (the repo at ${KIT}, a ".agents Protocol" kit of
skills, rules and sub-agents). The skill must let a coding agent, given a topic, reliably produce a
3Blue1Brown-grade NARRATED teaching video using Manim Community Edition (ManimCE): one run yields a
finished MP4 with a script, synthesized narration, and Manim animation synced to the narration.
"High quality" means it looks and teaches like 3Blue1Brown's videos, not merely renders.

Agreed path:
1. Build a corpus from the 3Blue1Brown neural-network / deep-learning series.
2. Analyze each video into a structured record of what he does and why it works.
3. Synthesize a framework: rules, a ManimCE pattern library, a quality checklist/rubric.
4. Build the skill using the superpowers "writing-skills" method (TDD for skills: baseline a subagent
   without the skill, watch it fail, write the skill, re-test) plus the "skill-creator" eval scripts.

Decisions already made (do not reopen):
- Target ManimCE. 3b1b's own code uses his fork ManimGL; idioms must be translated.
- Primary corpus = 3b1b's public Manim source + transcripts aligned per video section. Downloaded video
  keyframes are a secondary check. We write our own download/transcript/keyframe tooling (no 3rd-party plugin).
- The finished skill must bundle everything it needs (framework, pattern library, rubric, analyses, scripts).
- Narration provider is pluggable; a sensible default must be chosen and stated as an assumption.
- License: 3b1b/videos is CC BY-NC-SA 4.0. The framework derives principles and uses ORIGINAL ManimCE
  examples. Never copy his scene code into the skill.
- Follow the kit's rules (${KIT}/agents.md): git worktrees, look-it-up (cite sources, do not answer from
  memory when a source exists), minimal changes, delegate to subagents.

Environment facts:
- 3b1b source is cloned read-only at ${VIDEOS}. Series code: _2017/nn/part1.py, part2.py, part3.py
  (chapters 1-4, ~13k lines), _2024/transformers/*.py (~22k lines), shared infra in custom/,
  manim_imports_ext.py, custom_config.yml, stage_scenes.py; also _2026/cross_entropy/transformer_render.py.
- Network in THIS container: youtube.com, googlevideo.com, ytimg.com, 3blue1brown.com, docs.manim.community
  and 3b1b.github.io are BLOCKED (proxy answers 403). Public GitHub repos CAN be cloned anonymously over
  https (use GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/<owner>/<repo> /home/user/<owner>/<repo>).
  raw.githubusercontent.com and PyPI (https://pypi.org/pypi/<pkg>/json) are reachable. api.github.com is NOT
  usable. WebSearch/WebFetch tools may work; try them, and if they fail, say so. Never disable TLS, never
  route around a block; note blocked items under "unverified".
- Container: 4 CPUs, 15 GB RAM, ffmpeg installed; manim, yt-dlp, whisper, LaTeX NOT installed (PyPI works).
- A fresh session with the network unblocked will do the implementation; our job now is the DESIGN.

Hard rules for you:
- Do NOT modify anything under ${KIT} or ${VIDEOS}. Write only under ${OUT} (mkdir -p first) or clone
  under /home/user/<owner>/<repo>.
- Ground claims in evidence: cite file paths with line numbers, repo URLs you actually fetched, or mark
  the claim "unverified".
- Your final text IS the return value and is parsed by a program: return ONLY the structured output.

Markdown rules for every file you write (they will be committed to a repo gated by markdownlint, typos
and a link checker): exactly one H1 at the top line; ATX headings; blank lines before and after headings,
lists and fenced blocks; every fenced block names a language (text, bash, python, json, yaml); no trailing
spaces; no hard tabs outside code; no bare URLs (write <https://...> or [text](https://...)); only include
URLs you actually fetched or that are canonical repo/PyPI pages; unique heading text within a file;
ordered lists numbered 1. 2. 3.; file ends with one newline; spell correctly.
`

const MD_WRITE = (path) => `Write the full map as Markdown to ${path} (create the directory first).`

const READER_SCHEMA = {
  type: 'object',
  properties: {
    path: { type: 'string', description: 'absolute path of the markdown file written' },
    summary: { type: 'string', description: '5-10 sentences' },
    key_implications: { type: 'array', items: { type: 'string' }, description: '5-12 implications for the design' },
    blocked_or_unverified: { type: 'array', items: { type: 'string' } },
  },
  required: ['path', 'summary', 'key_implications'],
}

const READERS = [
  {
    key: '01-nn-2017-source',
    label: 'read:nn-2017',
    prompt: `${BRIEF}

# Your task: map the 2017 neural-network series source

Files: ${VIDEOS}/_2017/nn/part1.py, part2.py, part3.py (3.8k-4.7k lines each), network.py, playground.py,
plus ${VIDEOS}/_2017/gradient.py if it belongs to the series. Read part1.py fully in ~400-line chunks. For
part2.py and part3.py, first list every class with line numbers (grep -n '^class '), then read at least
half of each file, prioritizing the main explanatory scenes over utility classes. Use grep for frequency counts.

Produce a map with these sections, each with file:line evidence:
1. Scene inventory: table of scene class, what it visualizes, the teaching move it serves (hook, concrete
   example, abstraction, formula reveal, recap, aside), and roughly how long/complex it is.
2. Visual abstractions: reusable Mobjects/helpers (e.g., the network drawing class), what each encapsulates,
   what parameters it exposes, and how scenes compose them.
3. Color system: every named color constant used, the semantic role it plays (weights, activations, positive
   vs negative, emphasis, background), and how consistently roles map to colors.
4. Layout and composition: positions, scales, buff values, how formulas and diagrams share the frame, how many
   objects are typically on screen, where text sits relative to diagrams, use of frames/edges/corners.
5. Animation idioms: which Animation classes dominate (counts), run_time ranges, lag_ratio and rate_func use,
   how transitions between ideas are made (Transform vs ReplacementTransform vs FadeOut/FadeIn), updaters,
   indication/highlighting patterns, how emphasis is created and released.
6. Pacing and narrative structure: how a chapter sequences its ideas; what appears before any formula; how
   recaps are done; how long ideas get before the next; anything about wait() durations and narration sync.
7. Pi creatures and text: how the characters are used (reactions, questions), Tex/TexText usage, font sizes.
8. Explicit list of "the moves that make it good" you can infer from the code, each tied to evidence.
9. Counts table (grep-derived) of the most-used Manim names.

${MD_WRITE(`${OUT}/maps/01-nn-2017-source.md`)} Aim for 600-1500 lines.`,
  },
  {
    key: '02-transformers-2024-source',
    label: 'read:transformers-2024',
    prompt: `${BRIEF}

# Your task: map the 2024 transformer/attention/MLP series source

Files: ${VIDEOS}/_2024/transformers/*.py (~22k lines total). Strategy: read helpers.py and supplements.py
fully; for every other file, list all classes with line numbers (grep -n '^class '), then read at least 40%
of each file, prioritizing embedding.py, attention.py, mlp.py, network_flow.py and generation.py and the main
explanatory scenes. Also skim ${VIDEOS}/_2026/cross_entropy/transformer_render.py as the most recent example.

Produce the same map structure as a sibling reader does for the 2017 series (scene inventory; visual
abstractions; color system; layout; animation idioms with counts; pacing/narrative; text/Tex; "moves that make
it good"; counts table), each with file:line evidence, PLUS:
10. Evolution 2017 -> 2024: what changed in his style and tooling (3D, camera motion, data-driven scenes, use of
    real model weights/tokens, abstraction level, scene length), based on what you see in this code.
11. Data dependencies: which scenes depend on external data (model weights, token data, images) and how that
    constrains reproduction.

${MD_WRITE(`${OUT}/maps/02-transformers-2024-source.md`)} Aim for 600-1500 lines.`,
  },
  {
    key: '03-production-infrastructure',
    label: 'read:infra',
    prompt: `${BRIEF}

# Your task: map 3b1b's production infrastructure and workflow

Read fully: ${VIDEOS}/README.md, ${VIDEOS}/CLAUDE.md, ${VIDEOS}/manim_imports_ext.py,
${VIDEOS}/custom_config.yml, ${VIDEOS}/stage_scenes.py, everything under ${VIDEOS}/custom/ (including
characters/), ${VIDEOS}/sublime_custom_commands/, and skim ${VIDEOS}/once_useful_constructs/.
Also sample 3 recent project folders under ${VIDEOS}/_2025 and ${VIDEOS}/_2026 to confirm current conventions.

Map:
1. Rendering configuration: resolution, fps, background color, default fonts, Tex template/preamble, camera
   settings, output directories (from custom_config.yml and any config code).
2. Reusable production components: backdrops, end screens, logo, opening quotes, banners, Pi creatures
   (what each provides and how scenes use them).
3. The interactive development workflow (manimgl -se, checkpoint_paste) and what an agent-driven equivalent in
   ManimCE would need (fast preview loop, partial renders, scene-by-scene iteration).
4. How a video is assembled from scenes (stage_scenes.py, file organization, naming, ordering) and what that
   implies for a pipeline that aligns transcript sections to scene classes.
5. Conventions: imports, file layout per project, scene base classes, helper placement.
6. Anything about how narration and animation are coordinated in his process (from README/comments).

${MD_WRITE(`${OUT}/maps/03-production-infrastructure.md`)}`,
  },
  {
    key: '04-manimgl-to-manimce',
    label: 'read:manim-gap',
    prompt: `${BRIEF}

# Your task: the ManimGL -> ManimCE translation map and ManimCE capabilities

Steps:
1. Clone shallow: GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/3b1b/manim /home/user/3b1b/manim
   and GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/ManimCommunity/manim /home/user/ManimCommunity/manim
   (run them one at a time; allow up to 10 minutes each; if a directory already exists with a .git, reuse it).
2. From the series code (${VIDEOS}/_2017/nn and ${VIDEOS}/_2024/transformers and ${VIDEOS}/custom), collect the
   ~60 most-used Manim names (classes, methods, constants, animations) via grep frequency counts.
3. For each, find the ManimCE equivalent by reading the CE source under /home/user/ManimCommunity/manim/manim/
   and the docs source under /home/user/ManimCommunity/manim/docs/source/ (the docs website is blocked here).
   Record the ManimCE version from its pyproject.toml and the ManimGL version from its pyproject/setup.

Produce:
1. Translation table: ManimGL name -> ManimCE name/idiom -> gotchas, with source paths as evidence
   (Tex/TexText vs MathTex/Tex, InteractiveScene vs Scene, always/f_always vs add_updater/always_redraw,
   self.frame vs camera.frame/MovingCameraScene, Text/fonts, ThreeDScene, .animate syntax, run_time/lag_ratio,
   rate functions, color constants and palettes, VGroup/arrangement helpers, number/decimal mobjects,
   graphs/axes, matrices, Code, ImageMobject, SVG, groups, z-index/layering, backgrounds).
2. ManimCE features relevant to teaching videos: sections (next_section) and per-section render outputs,
   manim.cfg configuration, quality flags and render time implications, --format and output handling,
   OpenGL vs Cairo renderer status, caching/partial movie files, plugin mechanism, Text vs MarkupText vs Tex
   and LaTeX requirements (what breaks without LaTeX and the lightweight alternatives), 3D support.
3. Known pain points/gotchas when writing CE code programmatically (an agent will write it): common runtime
   errors, API changes across versions, performance traps.
4. A short list of CE idioms an agent must know to reproduce 3b1b-style moves (e.g., focus + dim the rest,
   morph formula to diagram, trace a path, animate a number).

${MD_WRITE(`${OUT}/maps/04-manimgl-to-manimce.md`)}`,
  },
  {
    key: '05-narration-sync-transcription-tooling',
    label: 'read:tooling',
    prompt: `${BRIEF}

# Your task: narration, sync, transcription and keyframe tooling options

Research, citing sources you actually fetched (GitHub clones, PyPI JSON, WebFetch if it works):
1. manim-voiceover (GitHub ManimCommunity/manim-voiceover): clone shallow to /home/user/ManimCommunity/manim-voiceover.
   Document: VoiceoverScene API, the voiceover context manager and tracker.duration, bookmarks
   (<bookmark mark='x'/> + wait_until_bookmark) and how word timing is obtained (whisper/stable-whisper),
   supported speech services (ElevenLabs, OpenAI, Azure, gTTS, pyttsx3, Coqui, recorder, others), caching,
   last release/commit date and ManimCE compatibility, licensing. Assess maintenance risk.
2. TTS options with quality/cost/offline trade-offs: Kokoro (hexgrad/kokoro on GitHub/PyPI; CPU feasibility,
   voices, license), Piper, edge-tts (terms of use risk), OpenAI TTS (models, pricing), ElevenLabs (quality,
   pricing, with-timestamps endpoint). Recommend a default for a CPU-only container and a premium option.
   Note whether each returns word/character timestamps.
3. Forced alignment for narration-to-animation sync: whisperx, stable-ts, aeneas, torchaudio CTC forced
   aligner: inputs, outputs, CPU cost, reliability on synthesized speech. Compare "TTS gives timestamps" vs
   "align afterwards" vs "manim-voiceover bookmarks".
4. Corpus transcription: yt-dlp subtitle flags (--write-subs --write-auto-subs --sub-langs en --sub-format
   json3/vtt --skip-download) and what auto-captions provide (word timings?), faster-whisper on CPU (speed
   per model size, word_timestamps), whisper.cpp. Which gives the best transcript for a 25-minute lecture?
5. Keyframe extraction: ffmpeg scene-change filter (select='gt(scene,T)') with showinfo to get timestamps,
   PySceneDetect (content detector), frame sampling at transcript-segment boundaries. Expected frame counts.
6. Video assembly: combining ManimCE section renders + narration audio with ffmpeg; loudness normalization;
   subtitle burn-in option.
Record for each tool: install method, dependencies (torch? espeak-ng?), model download hosts (huggingface.co,
etc. so they can be allow-listed), license, and your confidence.

${MD_WRITE(`${OUT}/maps/05-narration-sync-transcription-tooling.md`)}`,
  },
  {
    key: '06-kit-constraints-and-skill-authoring',
    label: 'read:kit+authoring',
    prompt: `${BRIEF}

# Your task: kit constraints and skill-authoring requirements

Read fully in ${KIT}: README.md, agents.md, agents.kit.md, CONTEXT.md, CHANGELOG.md, rules/*.md,
scripts/validate.sh, scripts/install.sh, .github/workflows/validate.yml, .markdownlint-cli2.jsonc, lychee.toml,
.typos.toml, .jscpd.json, .gitleaks.toml, .yamllint.yaml, docs/adr/*.md, docs/agents/*.md,
skills/research/SKILL.md, skills/code-review/*.md, agents/cr-planner/agent.md and one researcher agent.md.
Then read the superpowers writing-skills skill fully: ${WRITING_SKILLS}/SKILL.md,
${WRITING_SKILLS}/anthropic-best-practices.md, ${WRITING_SKILLS}/testing-skills-with-subagents.md,
${WRITING_SKILLS}/persuasion-principles.md, and ${WRITING_SKILLS}/examples/ (list and sample).
Then read ${SKILL_CREATOR}/SKILL.md, ${SKILL_CREATOR}/references/schemas.md and list ${SKILL_CREATOR}/scripts/
and ${SKILL_CREATOR}/agents/ (read their headers to learn what the eval loop does).

Produce:
1. The exact contract a new skill in this kit must satisfy: directory and file names, frontmatter keys and
   sorting, id rule, every check validate.sh performs. Pay special attention to the SLASH_REF and SKILL_CMD
   regexes: work out exactly which text patterns inside a SKILL.md or sibling .md (e.g. absolute paths like
   /home/user/x, URLs, CLI flags, "/tmp") would be flagged as unknown skill references, and how to write
   around them. Test your reading by running the validate script's logic mentally on sample strings.
2. What install.sh copies today (only *.md inside skills/<id>/) and the minimal change needed to ship
   scripts/ and references/ and other non-.md files with a skill, including effects on the CI install smoke
   test, the stamp manifest and --prune/--pull.
3. Every CI hygiene gate a new file must pass, with the concrete rule set in effect: markdownlint rules
   (which are disabled, which defaults still bite), lychee (every URL must resolve in CI), typos, jscpd
   (threshold and whether Python/shell scripts count), shellcheck/shfmt (shell scripts formatted with tabs?),
   gitleaks, yamllint/actionlint.
4. How the kit writes skills: structure, voice, length and delegation style of research and code-review
   SKILL.md; how skills reference agents in agents/ (frontmatter contract for agent.md); the no-model-pins
   and forge-agnostic ADRs; what the kit says about where research outputs go (docs/research/).
5. What writing-skills requires: TDD for skills (baseline subagent tests, RED/GREEN/REFACTOR), description
   = triggering conditions only, CSO/keyword guidance, size targets, flowchart policy, bundled scripts
   invoked via interpreter, testing-skills-with-subagents procedure, persuasion principles. What
   skill-creator adds: eval loop (run_eval.py, run_loop.py, grader/comparator agents), schemas, description
   improver. Propose how to combine both for this skill (which steps, in what order).
6. Where the corpus analyses, framework, pattern library, scripts, and generated videos should live
   (inside the skill vs docs/ vs outside the repo), with repo-size and license considerations.
7. Whether a new ADR is warranted (e.g., skills may ship scripts and reference corpora) and what it should say.
8. Any kit rule that constrains the design (worktrees, look-it-up, subagents, minimal-changes, comment-style,
   code-organization) and how the skill should honor it.

${MD_WRITE(`${OUT}/maps/06-kit-constraints-and-skill-authoring.md`)}`,
  },
  {
    key: '07-corpus-sources-inventory',
    label: 'read:corpus-sources',
    prompt: `${BRIEF}

# Your task: inventory the corpus sources for the neural-network series

1. Determine the video list of the 3Blue1Brown neural-networks topic: the four 2017 chapters, the 2024
   chapters (transformers/GPT, attention, how LLMs might store facts/MLP), "Large Language Models explained
   briefly", and anything newer in that topic. For each: title, YouTube ID if you can verify it, approximate
   duration, year, and the matching source files under ${VIDEOS} (map transcript topics to files/classes).
   YouTube and 3blue1brown.com are blocked here: try WebSearch/WebFetch; otherwise mark fields "unverified".
2. Site source repo: run git ls-remote https://github.com/3b1b/3Blue1Brown.com . If public, do a blobless
   partial clone: GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --no-checkout
   https://github.com/3b1b/3Blue1Brown.com /home/user/3b1b/3Blue1Brown.com ; then git sparse-checkout set
   the lessons content directory (find it via git ls-tree) and check out. Inspect the neural-network lesson
   folders: do they contain transcripts (format? timestamps?), article text (index.mdx), figures, video IDs,
   chapter timestamps? Document exact paths and formats with examples. If the repo is not public, say so.
3. Inventory the per-video artifacts a corpus pipeline can produce and the best source for each: source code
   (which files/classes), transcript (site repo vs YouTube captions via yt-dlp vs Whisper), keyframes
   (yt-dlp + ffmpeg), chapter markers (YouTube description), scene order (stage_scenes.py or class order).
4. Propose concretely how to align transcript sections to scene classes (class names vs transcript topics,
   order in file, visual matching of keyframes to scene renders, manual anchors) and estimate how reliable
   each is.
5. Data volume: total minutes, expected transcript size, keyframe counts at one frame per scene change, disk
   for 1080p downloads; what should and should not be committed to a git repo.
6. Licensing/terms notes for downloading and storing the videos for private analysis.

${MD_WRITE(`${OUT}/maps/07-corpus-sources-inventory.md`)}`,
  },
]

phase('Understand')
log('Understand: 7 readers mapping source, gap, tooling, kit constraints, corpus sources')
const maps = (await parallel(READERS.map(r => () =>
  agent(r.prompt, { label: r.label, phase: 'Understand', schema: READER_SCHEMA })
    .then(m => m && ({ key: r.key, ...m }))
))).filter(Boolean)
log(`Understand done: ${maps.length}/7 maps written`)
if (maps.length < 5) throw new Error(`Only ${maps.length} maps produced; aborting design`)

const MAP_LIST = maps.map(m => `- ${m.path}\n  summary: ${m.summary}`).join('\n')

const ARCH_SCHEMA = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    path: { type: 'string' },
    thesis: { type: 'string' },
    decisions_for_user: { type: 'array', items: { type: 'string' } },
  },
  required: ['name', 'path', 'thesis'],
}

const ARCH_SECTIONS = `
Required sections, in order, each specific and opinionated (concrete names, file paths, schemas, commands):
1. Thesis (what this design optimizes for and why).
2. System overview: components and data flow (text diagram), with the boundary of each unit, its inputs,
   outputs and dependencies, so each can be understood and tested alone.
3. Corpus pipeline: steps, tools, inputs/outputs per step, idempotency/resume, where data lives, what is
   committed vs kept local, how it runs in a fresh session with network access.
4. Per-video analysis method: who analyzes (subagents per video? per section?), the analysis record schema
   (fields), how it stays evidence-grounded (file:line, timestamps, keyframe refs), how it aligns transcript
   to code, how quality of the analyses is checked.
5. Framework representation: the files; how rules are phrased so an agent can apply AND check them; the
   pattern library (ManimCE idioms with original examples, how many, how organized); the quality rubric
   (what is scored, by whom, pass bar); how it stays within context budgets (progressive disclosure).
6. Skill design: SKILL.md outline, references/, scripts/; the run-time process topic -> script -> storyboard
   -> scenes -> narration -> sync -> render -> review -> MP4; verification loops (render checks, rubric
   self-review, frame review via image reading); error handling (render failures, LaTeX missing, TTS or
   network failures, long renders); render-time budget and quality tiers; what the skill asks the user and when.
7. Narration and sync: default TTS, premium option, alignment approach, manim-voiceover use or not and why.
8. Testing strategy: scripts (unit/integration), framework (does an agent given the framework produce
   rubric-passing scenes?), skill (writing-skills baseline vs with-skill subagent tests; skill-creator evals;
   a fixed test-prompt set; what "pass" means).
9. Repo layout inside the kit and required kit changes (install.sh, validate.sh, README, CHANGELOG, ADR).
10. Phasing/milestones with rough effort and what each milestone proves.
11. Risks and mitigations.
12. Deliberately cut (YAGNI) and why.
13. Decisions needed from the user.
Length 400-900 lines. Read ALL the maps before writing. Honor every decision in the brief.`

const ANGLES = [
  {
    key: 'corpus-fidelity',
    angle: `ANGLE: corpus fidelity first. Maximize what the framework learns from 3b1b: evidence-grounded,
systematic analysis of every scene; faithful translation of his moves into ManimCE; a rich pattern library.
The skill is only as good as the framework's fidelity.`,
  },
  {
    key: 'repeatable-process',
    angle: `ANGLE: repeatable process first. The skill's run-time process is king: determinism, explicit
verification loops, render reliability, never shipping a bad video, bounded context use, clear hand-offs
to subagents. The framework exists to serve the rubric and the process.`,
  },
  {
    key: 'minimal-viable',
    angle: `ANGLE: minimal viable, extensible. The smallest system that produces one narrated 3b1b-grade video
end to end in a fresh session; cut aggressively; defer anything not needed for the first good video; make
extension points explicit so corpus depth and tooling can grow later.`,
  },
]

phase('Design')
log('Design: 3 architects proposing from different angles')
const archs = (await parallel(ANGLES.map(a => () =>
  agent(`${BRIEF}

# Your task: propose a complete architecture

${a.angle}

Maps to read in full first (they are your evidence base):
${MAP_LIST}

${ARCH_SECTIONS}

Write the architecture to ${OUT}/architectures/${a.key}.md (mkdir -p first). Return name, path, thesis and
decisions_for_user.`, { label: `architect:${a.key}`, phase: 'Design', schema: ARCH_SCHEMA, effort: 'high' })
    .then(r => r && ({ key: a.key, ...r }))
))).filter(Boolean)
log(`Design done: ${archs.length}/3 architectures`)
if (archs.length < 2) throw new Error('Fewer than 2 architectures; aborting')

const ARCH_LIST = archs.map(a => `- ${a.path} (${a.name}): ${a.thesis}`).join('\n')

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    path: { type: 'string' },
    ranking: { type: 'array', items: { type: 'string' } },
    top_ideas_to_graft: { type: 'array', items: { type: 'string' } },
  },
  required: ['path', 'ranking'],
}

const LENSES = [
  {
    key: 'animation-practitioner',
    lens: `LENS: animation and pedagogy practitioner. Judge whether each design would actually capture what
makes 3b1b's videos good visually and pedagogically, and whether its framework would transfer that to an
agent writing ManimCE. Be skeptical of frameworks that are lists of platitudes.`,
  },
  {
    key: 'agent-reliability',
    lens: `LENS: agent reliability and skill authoring. Judge whether an agent following each skill would
behave consistently: context budget and progressive disclosure, failure modes, verification loops that
really catch bad output, ambiguity in instructions, compliance with writing-skills and skill-creator
practice, testability of the skill itself.`,
  },
  {
    key: 'shipping-engineer',
    lens: `LENS: pragmatic shipping engineer. Judge effort, dependency and maintenance risk (ManimCE
versions, TTS services, LaTeX, model downloads), CPU-only render and transcription times, CI gates, repo
size, licensing, and whether milestones prove the right things early.`,
  },
]

phase('Judge')
log('Judge: 3 judges scoring the architectures')
const judgments = (await parallel(LENSES.map(l => () =>
  agent(`${BRIEF}

# Your task: judge the candidate architectures

${l.lens}

Read fully: the architectures
${ARCH_LIST}
and, for feasibility checks, these maps:
${MAP_LIST}

Score each architecture 1-10 on: (1) output-quality fidelity, (2) repeatability, (3) feasibility under the
stated constraints, (4) corpus leverage and evidence grounding, (5) fit with kit conventions and skill
authoring best practice, (6) testability, (7) simplicity/YAGNI. One-sentence justification per score, then
a total. For each architecture list strengths, weaknesses, factual errors or unverified claims, and the
best ideas worth grafting into a synthesis. End with a ranking and a short note on what NONE of them handles.

Write to ${OUT}/judgments/${l.key}.md (mkdir -p first). Return path, ranking, top_ideas_to_graft.`,
    { label: `judge:${l.key}`, phase: 'Judge', schema: JUDGE_SCHEMA, effort: 'high' })
    .then(r => r && ({ key: l.key, ...r }))
))).filter(Boolean)
log(`Judge done: ${judgments.length}/3 judgments`)

const JUDGE_LIST = judgments.map(j => `- ${j.path}: ranking ${JSON.stringify(j.ranking)}`).join('\n')

const SYNTH_SCHEMA = {
  type: 'object',
  properties: {
    path: { type: 'string' },
    recommended_approach: { type: 'string' },
    approaches: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, one_line: { type: 'string' } }, required: ['name', 'one_line'] } },
    decisions_for_user: { type: 'array', items: { type: 'string' } },
    assumptions: { type: 'array', items: { type: 'string' } },
  },
  required: ['path', 'recommended_approach', 'approaches'],
}

phase('Synthesize')
log('Synthesize: writing the design proposal')
const synth = await agent(`${BRIEF}

# Your task: synthesize the final design proposal for the human to approve

Read fully, in this order: the judgments
${JUDGE_LIST}
the architectures
${ARCH_LIST}
and the maps
${MAP_LIST}

Write ${OUT}/design-proposal.md: a proposal the project owner will read and approve section by section.
Structure (use these headings):
1. H1 title; then a line "Status: PROPOSAL, awaiting owner approval (brainstorming step 5)".
2. Context and goal (short; restate the brief's goal and decisions in a few lines).
3. Approaches considered: 2-3 approaches with trade-offs, then "Recommendation" naming one and why, grafting
   the judges' best ideas; make clear what was taken from each.
4. Design, as self-contained sections of 100-400 words each with concrete names, paths, schemas and commands:
   Architecture overview; Components (what it does, how you use it, what it depends on); Data flow; Corpus
   pipeline; Analysis record schema; Framework representation (rules, pattern library, rubric); Skill
   structure and run-time process; Narration and sync; Error handling; Testing; Repo layout and kit changes;
   Phasing and milestones.
5. Assumptions (explicit, numbered; include the TTS default and the video-length default).
6. Decisions needed from the owner (only those that materially change the work).
7. Risks and mitigations.
8. Open questions (things no map could verify, e.g. because of blocked hosts).
Resolve contradictions between architectures; do not present unverified claims as facts (say "unverified").
Respect every decision in the brief and the YAGNI principle. Return path, recommended_approach, approaches,
decisions_for_user, assumptions.`, { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA, effort: 'high' })
if (!synth) throw new Error('Synthesis failed')
log(`Proposal written: ${synth.path}`)

const CRITIC_SCHEMA = {
  type: 'object',
  properties: {
    path: { type: 'string' },
    verdict: { type: 'string' },
    gaps: { type: 'array', items: { type: 'object', properties: { gap: { type: 'string' }, severity: { type: 'string' }, suggestion: { type: 'string' } }, required: ['gap', 'severity'] } },
  },
  required: ['path', 'gaps'],
}

log('Critique: adversarial completeness check')
const critique = await agent(`${BRIEF}

# Your task: adversarially critique the design proposal

Read ${synth.path} fully, then the maps:
${MAP_LIST}
and skim the judgments:
${JUDGE_LIST}

Find everything wrong or missing. Check specifically: (a) components or steps the proposal needs but never
defines; (b) claims presented as facts that the maps mark unverified or contradict; (c) internal
contradictions; (d) scope creep against YAGNI, and the opposite: cuts that make the first video impossible;
(e) violations of the brief's fixed decisions or the kit's rules and skill-authoring practice (description =
triggers only, SKILL.md size, bundled scripts invoked via interpreter, install.sh coverage, validate.sh
slash-ref false positives on paths in markdown); (f) feasibility holes: CPU render time at 1080p for a
5-15 minute video, LaTeX availability, TTS and model downloads, transcription time, context budget of the
run-time process; (g) licensing (CC BY-NC-SA source, TTS terms); (h) testability: can each milestone be
verified; (i) the owner's ability to approve: is anything ambiguous or interpretable two ways?
Rate each gap severity: blocker, major, minor. Write to ${OUT}/critique.md. Return path, verdict, gaps.`,
  { label: 'critic', phase: 'Synthesize', schema: CRITIC_SCHEMA, effort: 'high' })

const REVISE_SCHEMA = {
  type: 'object',
  properties: { path: { type: 'string' }, changes_made: { type: 'array', items: { type: 'string' } } },
  required: ['path'],
}

log('Revise: applying the critique to the proposal')
const revision = await agent(`${BRIEF}

# Your task: revise the design proposal using the critique

Read ${synth.path} and ${critique ? critique.path : OUT + '/critique.md'} fully, then consult the maps as needed:
${MAP_LIST}

Fix every blocker and major gap in place in ${synth.path} (use Edit; keep the heading structure and the
markdown rules). Fix minors when cheap. Where a gap cannot be resolved from evidence, convert the claim into
an explicit assumption, open question, or decision for the owner rather than deleting it. Append a final
section "## Revision notes" listing each change in one line. Return path and changes_made.`,
  { label: 'revise', phase: 'Synthesize', schema: REVISE_SCHEMA, effort: 'high' })

return {
  maps: maps.map(m => ({ key: m.key, path: m.path, summary: m.summary, key_implications: m.key_implications, blocked_or_unverified: m.blocked_or_unverified || [] })),
  architectures: archs,
  judgments,
  proposal: synth,
  critique,
  revision,
}
