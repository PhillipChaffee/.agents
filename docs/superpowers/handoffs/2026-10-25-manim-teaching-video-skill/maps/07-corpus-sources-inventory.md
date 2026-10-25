# Corpus Sources Inventory: 3Blue1Brown Neural-Network Series

This map inventories every source a corpus pipeline can draw on for the
3Blue1Brown neural-network topic: the video list, the public site repository,
the public figure bucket, the animation source code, and the tooling needed
to download, transcribe and keyframe the videos. It was compiled on
2026-10-25 from a container in which YouTube and 3blue1brown.com are blocked,
so every YouTube-side fact is marked by how it was established.

## Scope and evidence legend

Evidence markers used throughout:

- **Verified**: read from a file on disk (path and line cited), from a
  repository fetched over git, or from an HTTP response observed here.
- **Inferred**: deduced from verified evidence (for example a scene class
  name matched to an article section); the reasoning is given.
- **Third-party**: reported by a WebSearch result snippet that could not be
  opened (WebFetch failed with DNS errors for every non-GitHub host tried).
- **Unverified**: could not be checked from this container; the
  implementation session must confirm it.

Local inputs inspected:

- `/home/user/3b1b/videos` (read-only clone of the 3b1b `videos` repository,
  shallow, HEAD `306a134`, merge of PR #150 dated 2026-09-29).
- `/home/user/3b1b/3Blue1Brown.com` (blobless sparse clone made for this map,
  HEAD `7c93d6391b808309d1c4b9b8c13ffbf613d74a3b`).
- The public Google Cloud Storage bucket that hosts the site's lesson assets
  (HTTP 200 on object GET and on XML listing; see section 2).

Gate status of this file on 2026-10-25: `markdownlint-cli2` 0.18.1 with the
kit's `.markdownlint-cli2.jsonc` reports 0 errors, `typos` with the kit's
`.typos.toml` is clean, and `lychee` is not installed in this container, so
link targets were checked with `curl` instead (section 7, item 10).

## 1. Video list

The canonical ordering is the `neural-networks` entry of
`app/data/topics.json` in the site repository (verified). It lists eleven
lesson slugs, in this order: `neural-networks`, `gradient-descent`,
`neural-network-analysis`, `backpropagation`, `backpropagation-calculus`,
`mini-llm`, `gpt`, `attention`, `mlp`, `cross-entropy`, `diffusion-models`.

Every YouTube ID and date below is **verified** from the `video:` and `date:`
frontmatter fields of `app/pages/lessons/<year>/<slug>/index.mdx`; the
`source:` column is the frontmatter `source:` field, which the site turns
into a link to `3b1b/videos` (`Lesson.tsx`, the `source` link block).
Durations are **third-party** (minute-rounded figures from course and
episode listings surfaced by WebSearch) and must be confirmed with
`yt-dlp --print duration` once YouTube is reachable. A WebSearch retry on
2026-10-25 surfaced no duration for either 2026 video, and a WebFetch of a
YouTube watch page failed with a DNS error (`ENOTFOUND www.youtube.com`),
so those two stay unverified.

| # | Slug | Site title (frontmatter) | YouTube ID | Date | Duration | `source:` |
| --- | ------ | -------------------------- | ------------ | ------ | ---------- | ----------- |
| 1 | `neural-networks` | But what is a Neural Network? | `aircAruvnKk` | 2017-10-05 | ~19 min | `_2017/nn/part1.py` |
| 2 | `gradient-descent` | Gradient descent, how neural networks learn | `IHZwWFHWa-w` | 2017-10-16 | ~21 min | `_2017/nn/part2.py` |
| 3 | `neural-network-analysis` | Analyzing our neural network | none (text-only lesson) | 2017-10-16 | n/a | none |
| 4 | `backpropagation` | What is backpropagation really doing? | `Ilg3gGewQ5U` | 2017-11-03 | ~14 min | `_2017/nn/part3.py` |
| 5 | `backpropagation-calculus` | Backpropagation calculus | `tIeHLnjs5U8` | 2017-11-03 | ~10 min | `_2017/nn/part3.py` |
| 6 | `mini-llm` | Large Language Models explained briefly | `LPZh9BOjkQs` | 2024-11-20 | ~8-9 min | `_2024/transformers/` |
| 7 | `gpt` | Transformers, the tech behind LLMs (Deep Learning Chapter 5) | `wjZofJX0v4M` | 2024-04-01 | ~27 min | `_2024/transformers/` |
| 8 | `attention` | Attention in transformers, step-by-step (Deep Learning Chapter 6) | `eMlx5fFNoYc` | 2024-04-07 | ~26 min | `_2024/transformers/` |
| 9 | `mlp` | How might LLMs store facts (Deep Learning Chapter 7) | `9-Jl0dxWQs8` | 2024-08-31 | ~23 min | `_2024/transformers/` |
| 10 | `cross-entropy` | But what is Cross-Entropy? (Compression is Intelligence Part 2) | `GlYgs6v2YfU` | 2026-07-16 | unverified | `_2026/cross_entropy/` |
| 11 | `diffusion-models` | But how do AI images and videos actually work? (guest video by Welch Labs) | see note below | 2025-07-25 | unverified | none |

Row 11's ID is in `app/pages/lessons/2025/diffusion-models/index.mdx`; it is
not reproduced here because the `typos` checker misreads one of its letter
groups as a misspelling, and the video is excluded from the corpus anyway.

Related lessons that exist in the repository but are not in the topic list:

| Slug | Site title | YouTube ID | Date | `source:` | Note |
| ------ | ------------ | ------------ | ------ | ----------- | ------ |
| `2026/entropy` | Reinventing Entropy (Compression is Intelligence Part 1) | `l6DKRf-fAAM` | 2026-06-07 | `_2026/cross_entropy/` | Same code directory as row 10 |
| `2024/transformers-talk` | Visualizing transformers and attention (TNG Big Tech Day 2024 talk) | `KJtZARuO3JY` | 2024-11-20 | none | Live talk, no Manim source |

Original YouTube upload titles differ from the site titles (**third-party**,
from WebSearch snippets): the 2017 uploads carry the suffix "Deep learning,
chapter N" with N = 1 to 4, and the 2024 uploads were titled "But what is a
GPT? Visual intro to Transformers", "Attention in transformers, visually
explained", "How might LLMs store facts" and "Large Language Models explained
briefly". Treat the YouTube title as metadata to capture with
`--write-info-json`, not as a key.

### Chapter-number mismatch

The site numbers chapters with the text-only "Analyzing our neural network"
as chapter 3 (`chapter: 3` in its frontmatter), so the two backpropagation
lessons are `chapter: 4` and `chapter: 5` on the site while their YouTube
titles say chapters 3 and 4 (verified frontmatter versus third-party titles).
The 2024 lessons carry chapter numbers 5, 6 and 7 inside their titles rather
than in a `chapter:` field. Any corpus record should store both the site
chapter and the YouTube chapter to avoid confusion.

### Recommended corpus tiers

1. **Primary (eight narrated videos with Manim source):** rows 1, 2, 4, 5,
   6, 7, 8 and 9. About 149 minutes in total using the third-party
   durations. These are the videos whose source, article, figures and
   narration can all be cross-referenced.
2. **Secondary (same topic, source present, newest idioms):** rows 10 and
   `entropy`. Their `index.mdx` files are frontmatter-only (9 lines, no body,
   no figures; the bucket prefixes `lessons/2026/entropy/` and
   `lessons/2026/cross-entropy/` hold zero objects), so only video and code
   are available. Their code (`_2026/cross_entropy/`, 16,665 lines) is the
   most recent ManimGL style in the corpus and is useful for the pattern
   library even if the videos are analyzed less deeply.
3. **Exclude:** row 11 (guest video, not Grant Sanderson's narration or
   animation, no source) and `transformers-talk` (a recorded live talk).

## 2. Site source repository

### Access and clone commands

`git ls-remote https://github.com/3b1b/3Blue1Brown.com` succeeded
anonymously (verified): HEAD and `main` are
`7c93d6391b808309d1c4b9b8c13ffbf613d74a3b`; other branches include
`stats-update`, `translation-page`, `webkit-update`, `showcase-translations`,
`Exa-Talent-Page` and `copilot/content-issues-review`. The repository is
public. The clone used for this map:

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --no-checkout \
  https://github.com/3b1b/3Blue1Brown.com /home/user/3b1b/3Blue1Brown.com
cd /home/user/3b1b/3Blue1Brown.com
git sparse-checkout set app/pages/lessons app/data
git sparse-checkout add app/util app/components
git checkout main
```

The full tree has 862 paths (`git ls-tree -r --name-only HEAD | wc -l`).
Top level: `app/`, `bucket/`, `public/`, `tests/`, `AGENTS.md`, `CLAUDE.md`,
`License.md`, `README.md`, `package.json`, `vite.config.ts`,
`react-router.config.ts`, `netlify.toml`. `AGENTS.md` describes the stack
(Bun, React Router v7 in framework mode, MDX with remark math, MathJax,
Netlify) and the layout: `/app/pages` is "hierarchy of site's pages and
content/components/assets/data/etc. specific to each of them".

### Lesson folder layout

Lessons live at `app/pages/lessons/<year>/<slug>/index.mdx`, one folder per
lesson, optionally with `patrons.txt` and lesson-specific components
(verified). Years 2015 to 2026 are present. The neural-network folders under
`app/pages/lessons/`:

```text
2017/neural-networks/          index.mdx NeuralNetwork.jsx data.js patrons.txt
2017/gradient-descent/         index.mdx patrons.txt
2017/neural-network-analysis/  index.mdx
2017/backpropagation/          index.mdx patrons.txt
2017/backpropagation-calculus/ index.mdx patrons.txt
2024/gpt/                      index.mdx patrons.txt
2024/attention/                index.mdx patrons.txt
2024/mlp/                      index.mdx patrons.txt
2024/mini-llm/                 index.mdx patrons.txt
2024/transformers-talk/        index.mdx
2026/entropy/                  index.mdx
2026/cross-entropy/            index.mdx
```

The public URL of a lesson is `/lessons/<slug>` on the site host; the route
is derived in `react-router.config.ts` (lines 15-24) by capturing
`lessons/20[0-9][0-9]/(.*)/index.mdx`, so the year is not part of the URL.
WebSearch result listings (third-party) show live addresses of exactly that
form for `cross-entropy`, `entropy` and `diffusion-models`.

### Frontmatter schema

`app/pages/lessons/lessons.ts` lines 8-22 define `RawLessonFrontmatter`:
`id`, `title`, `date`, `description`, `credits` (string list of
"Role by Name"), `video` (YouTube ID), `source` (path inside `3b1b/videos`),
`chapter` (number), `image`, `thumbnail`, `combinedCredits`, `readable`,
`interactive`. `vite.config.ts` lines 48-63 append `readable` (body longer
than 500 characters) and `interactive` (body contains `<Interactive`) at
build time. Example from
`app/pages/lessons/2017/neural-networks/index.mdx` lines 1-11, with the long
`description:` line omitted:

```yaml
---
title: But what is a Neural Network?
date: 2017-10-05
chapter: 1
video: aircAruvnKk
source: _2017/nn/part1.py
credits:
  - Lesson by Grant Sanderson
  - Text adaptation by Josh Pullen
---
```

`lessons.ts` lines 32-58 derive `year` from `date` and the card image from
the video ID (through `getThumbnail` in `app/components/YouTube.tsx`, which
builds the YouTube `maxresdefault.jpg` thumbnail URL from the ID).

Parser notes (verified by grep over the twelve frontmatters): `date:` is a
bare YAML date in the 2017 and 2024 lessons but a quoted string in both 2026
lessons (`2026/entropy/index.mdx` line 4, `2026/cross-entropy/index.mdx`
line 4); `chapter:` appears only in the 2017 lessons; `video:` is absent from
`neural-network-analysis`; and `source:` names a file for 2017 but a
directory for 2024 and 2026. A pipeline must read `date` as a string and
treat `video`, `chapter` and `source` as optional.

### Transcripts

No transcript exists for any neural-network lesson (verified: the only
transcript file in the whole tree is
`app/pages/lessons/2017/higher-order-derivatives/transcript.txt`, 34 lines,
4,652 bytes, and no code under `app/util`, `app/components` or
`Lesson.tsx` references transcripts). That lone file shows the format the
site once used: a two-level outline with a section label per top-level
bullet and one tab-indented bullet per spoken paragraph, with no timestamps:

```text
- <Section label>
    - <First spoken paragraph of the section.>
    - <Next spoken paragraph.>
- <Next section label>
```

Conclusion: transcripts must come from YouTube captions or from speech
recognition (section 3).

### Article text

Each `index.mdx` body is a prose adaptation of the video credited as "Text
adaptation by Josh Pullen" (2017) or "Text adaptation by Justin Sun" (2024),
not a verbatim transcript (verified credits). Sizes (verified with `wc`):

| Lesson | Lines | Words | Bytes | `<Figure>` | `##` headings |
| -------- | ------- | ------- | ------- | ------------ | ---------------- |
| 2017/neural-networks | 440 | 4,725 | 29,436 | 36 | 6 |
| 2017/gradient-descent | 314 | 2,899 | 18,416 | 26 | 2 |
| 2017/backpropagation | 303 | 2,657 | 17,457 | 24 | 6 |
| 2017/backpropagation-calculus | 456 | 3,518 | 26,870 | 17 | 3 |
| 2024/gpt | 272 | 4,050 | 25,049 | 22 | 6 |
| 2024/attention | 545 | 5,298 | 33,467 | 56 | 1 |
| 2024/mlp | 428 | 4,548 | 28,643 | 44 | 1 |
| 2024/mini-llm | 188 | 1,463 | 9,593 | 20 | 4 |
| 2017/neural-network-analysis | 113 | 1,235 | 7,707 | n/a | n/a |

Total for the eight video articles: 29,158 words, about 189 KB of MDX.
Components used (occurrence counts across the four largest articles):
`<Figure` 158, `<Question` 12, `<Collapsible` 7, `<LessonLink` 4,
`<Interactive` 1, `<FreeResponse` 1. Section headings are sparse in the
2024 articles (one `##` in `attention` and `mlp`), so headings alone cannot
drive sectioning; figure captions and paragraphs must.

Example headings, `2024/gpt/index.mdx`: "What is a GPT model?", "Premise of
Deep Learning", "Embedding", "Unembedding", "Unembedding Matrix", "Softmax".
`2017/neural-networks/index.mdx`: "The Structure of a Neural Network", "Why
Use Layers?", "How Information Passes Between Layers", "More Compact
Notation", "The Network Is Just a Function", "Next up: Learning!".

### Figures and the public bucket

Figures are referenced as `<Figure image="$lesson/<name>.jpg" />` or with a
caption as children, and some as `<Figure video="$lesson/<name>.mp4" />`
(verified; `Figure.tsx` renders image, video, or tabs for both).
`vite.config.ts` lines 67-77 replace `$lesson` with
`${site.gcp.bucket}/lessons/<year>/<slug>`, and `app/data/site.json` sets
`gcp.bucket` to <https://storage.googleapis.com/3blue1brown-website-bucket>.
The site repository's `bucket/` folder holds only sync scripts;
`bucket/pull.sh` runs `rclone sync gcs:3blue1brown-website-bucket/lessons
./lessons`, and `bucket/.gitignore` ignores `lessons`, so figure binaries
are never in git.

The bucket is publicly readable (verified on 2026-10-25): an object GET
returned `200 image/jpeg` (67,798 bytes for
`lessons/2017/neural-networks/three-3s.jpg`), and the S3-compatible XML
listing `?prefix=lessons/<year>/<slug>/&max-keys=1000` returned 200 with
`<Key>`, `<Size>`, `<LastModified>` and `<ETag>` per object. Per-lesson
inventory from those listings:

| Prefix | Objects | MB | Composition |
| -------- | --------- | ---- | ------------- |
| `lessons/2017/neural-networks/` | 72 | 35.8 | 31 png, 28 jpg, 9 mp4, 2 js, 1 svg, 1 txt |
| `lessons/2017/gradient-descent/` | 54 | 32.6 | 24 jpg, 24 png, 5 mp4, 1 txt |
| `lessons/2017/backpropagation/` | 46 | 24.8 | 22 jpg, 22 png, 1 mp4, 1 txt |
| `lessons/2017/backpropagation-calculus/` | 29 | 5.1 | 11 jpg, 11 png, 4 svg, 2 mp4, 1 txt |
| `lessons/2024/gpt/` | 49 | 23.3 | 24 jpg, 24 png, 1 txt |
| `lessons/2024/attention/` | 129 | 74.4 | 64 jpg, 64 png, 1 txt |
| `lessons/2024/mlp/` | 96 | 42.5 | 47 jpg, 47 png, 1 jpeg, 1 txt |
| `lessons/2024/mini-llm/` | 43 | 32.7 | 21 jpg, 21 png, 1 txt |
| `lessons/2026/entropy/` | 0 | 0 | empty |
| `lessons/2026/cross-entropy/` | 0 | 0 | empty |

Totals for the eight primary lessons: 518 objects, 271.2 MB. Every jpg has a
png twin (the png is the larger master; the jpg is what the article
references), and the `.txt` in each prefix is a copy of `patrons.txt`
(verified by fetching `lessons/2024/gpt/patrons.txt`: a list of names), not
a transcript. The 17 mp4 clips in the 2017 prefixes are short animation
loops referenced through `<Figure video=...>`.

Why this matters: the figures are frames exported from the videos and each
sits next to the article paragraph it illustrates, so they form a curated,
captioned keyframe set (245 `<Figure>` tags across the eight articles) that
needs no scene detection and that anchors article text to visual moments.

### Video IDs and chapter timestamps

Video IDs come only from frontmatter `video:`; `Lesson.tsx` builds the embed
URL and a schema.org `VideoObject` from it. The `YouTube` component accepts a
`time` prop (`YouTube.tsx`, `getWatch(id, time)`), but no neural-network
article uses `time=` or embeds a second `<YouTube>` (verified by grep), and
no `mm:ss` pattern occurs in any of the ten articles. The repository holds
no chapter markers; those must come from the YouTube description via
`yt-dlp --write-info-json` (section 3).

### Site license

`License.md` (verified): "Copyright 2021-2026 3Blue1Brown LLC. All rights
reserved." Reproduction, distribution, modification and derivative works
require written permission; "Viewing this repository on GitHub or running it
locally for personal, non-commercial evaluation is permitted." Article text
and bucket figures are therefore private-analysis inputs only and must not
be committed to or shipped with the skill (section 6).

## 3. Per-video artifacts and best sources

| Artifact | Best source | Fallback | Status |
| ---------- | ------------- | ---------- | -------- |
| Scene source code | `3b1b/videos` files named in frontmatter `source:` (section 1) | none needed | Verified, on disk |
| Scene order | Definition order in each file (`stage_scenes.py` logic) | manual reorder | Verified logic, inferred per video |
| Article text | `index.mdx` body | none | Verified, on disk |
| Captioned figures | Bucket objects per lesson prefix | `<Figure>` tags in MDX | Verified, public |
| Transcript | YouTube captions via `yt-dlp --write-subs --write-auto-subs` | Whisper on downloaded audio | Unverified (YouTube blocked) |
| Chapter markers | `info.json` `chapters` and `description` from yt-dlp | article `##` headings | Unverified |
| Keyframes | yt-dlp 1080p download + ffmpeg scene detection | bucket figures | ffmpeg path verified locally |
| Thumbnail | `yt-dlp --write-thumbnail` or the `maxresdefault.jpg` pattern used by `YouTube.tsx` | none | Unverified |
| Duration, title, upload date | `info.json` | third-party listings | Unverified |

### Source code

The code is the primary corpus by decision. Inventory (verified with
`wc -l` and `grep -c '^class '`):

| File | Lines | Classes | Pi/teacher scenes | Other non-content | `self.play(` |
| ------ | ------- | --------- | ------------------- | ------------------- | -------------- |
| `_2017/nn/part1.py` | 4,664 | 55 | 14 | 1 external, 2 thumbnail/end, 7 helper mobjects | 275 |
| `_2017/nn/part2.py` | 3,791 | 61 | 14 | 4 external, 5 TODO stubs, 1 end, 1 helper | 189 |
| `_2017/nn/part3.py` | 4,496 | 35 | 12 | 3 external, 5 TODO stubs, 3 thumbnail/end | 331 |
| `_2024/transformers/generation.py` | 986 | 24 | 0 | 0 | 19 |
| `_2024/transformers/embedding.py` | 3,047 | 30 | 0 | 0 | 144 |
| `_2024/transformers/ml_basics.py` | 2,430 | 14 | 0 | 0 | 140 |
| `_2024/transformers/network_flow.py` | 1,531 | 14 | 0 | 1 thumbnail | 74 |
| `_2024/transformers/attention.py` | 4,093 | 20 | 0 | 0 | 216 |
| `_2024/transformers/mlp.py` | 2,627 | 16 | 0 | 0 | 184 |
| `_2024/transformers/chm.py` | 2,160 | 38 | 3 | 2 thumbnail/end | 98 |
| `_2024/transformers/supplements.py` | 2,252 | 79 | 36 | 2 end screens | 189 |
| `_2024/transformers/helpers.py` | 819 | 10 | n/a (mobject and animation helpers only) | n/a | n/a |
| `_2024/transformers/auto_regression.py` | 599 | 10 | 0 | byte-identical to `old_auto_regression.py` (`cmp`), superseded by `generation.py` | n/a |
| `_2024/transformers/almost_orthogonal.py` | 51 | 0 | n/a (torch experiment, no scenes) | n/a | n/a |
| `_2026/cross_entropy/entropy.py` | 2,446 | 10 | 0 | 0 | 131 |
| `_2026/cross_entropy/language_models.py` | 1,998 | 16 | 0 | 0 | 102 |

"Pi/teacher scenes" are classes inheriting `TeacherStudentsScene` or
`PiCreatureScene` (interstitial reaction shots). "External" means
`ExternallyAnimatedScene` (`custom/filler.py` line 4), a placeholder for
footage made outside Manim (the 2017 cost-surface shots, for example
`part2.py` lines 1926, 2139 and 2568). TODO stubs are `TODOStub`
placeholders for inserts of earlier scenes (`part2.py` lines 2571, 2722,
2968, 3264, 3269; `part3.py` lines 35-50, 418).

Video to file and class mapping:

- **Chapter 1** (`part1.py`, verified by frontmatter): whole file. Content
  arc by class order: digit example (`ExampleThrees` 336),
  `LayOutPlan` 619, `PreviewMNistNetwork` 784, `BreakDownName` 929,
  `IntroduceEachLayer` 1036, `BreakUpMacroPatterns` 1488,
  `SecondLayerIsLittleEdgeLayer` 1876, `IntroduceWeights` 2237,
  `MotivateSquishing` 2619, `IntroduceSigmoid` 2717, `IncludeBias` 2780,
  `ShowRemainingNetwork` 3017, `IntroduceWeightMatrix` 3334,
  `NeuronIsFunction` 3947, `NextVideo` 4141, then post-credit ReLU material
  (`IntroduceReLU` 4368, `CompareSigmoidReLUOnDeepNetworks` 4470).
- **Chapter 2** (`part2.py`): whole file. `PreviewLearning` 142,
  `TrainingVsTestData` 330, `IntroduceCostFunction` 585,
  `SingleVariableCostFunction` 1440, `GradientDescentAlgorithm` 1946,
  `ShowFullCostFunctionGradient` 1974, `NonSpatialGradientIntuition` 2157,
  `GradientNudging` 2576, `TestPerformance` 2772,
  `InterpretFirstWeightMatrixRows` 2998, `InputRandomData` 3090,
  `CompareLearningCurves` 3616.
- **Chapters 3 and 4 on YouTube** (`part3.py`, both frontmatters point to
  this one file): inferred split at `EOCWrapper` line 2083 and
  `SimplestNetworkExample` line 2094. Lines 5-2082 (`LayOutPlan`,
  `InterpretGradientComponents` 55, `ShowAveragingCost` 423,
  `WalkThroughTwoExample` 545, `ConstructGradientFromAllTrainingExamples`
  1463, `OrganizeDataIntoMiniBatches` 1868) are "What is backpropagation
  really doing?"; lines 2083-4290 (`SimplestNetworkExample`,
  `GeneralFormulas` 3641, `LayersOfComplexity` 4223) are "Backpropagation
  calculus". The thumbnails confirm the split: `Thumbnail` 4415 is titled
  "Backpropagation" and `SupplementThumbnail` 4462 "Backpropagation
  calculus".
- **GPT (chapter 5)**: inferred from class names versus article headings.
  Autoregression and chatbot framing: `generation.py` (lines 112-986).
  Deep-learning premise, GPT-3 parameter counts, softmax, cost function:
  `ml_basics.py` (`PremiseOfML` 392, `LinearRegression` 1036,
  `ShowGPT3Numbers` 1174, `DistinguishWeightsAndData` 1666,
  `SoftmaxBreakdown` 1814, `CostFunction` 2368). Tokens and embeddings:
  `embedding.py` (`IntroduceEmbeddingMatrix` 341, `Word2VecScene` family
  612-1710, `DotProducts` 1724, `RicherEmbedding` 2081). Overall flow and
  unembedding: `network_flow.py` (`HighLevelNetworkFlow` 7,
  `MentionContextSizeAndUnembedding` 723). Interstitials:
  `supplements.py` lines 9-834 (`GPTInitials`, `GamePlan`, `EndScreen`).
- **Attention (chapter 6)**: `attention.py` whole file (`AttentionPatterns`
  10, `QueryMap` 1715, `KeyMap` 1839, `DescribeAttentionEquation` 1850,
  `ShowMasking` 2169, `IntroduceValueMatrix` 2313, `CountMatrixParameters`
  2561, `LowRankTransformation` 3014, `CrossAttention` 3120,
  `MultiHeadedAttention` 3503, `OutputMatrix` 3897, `Parallelizability`
  4036) plus `supplements.py` lines 841-1338 (`HighlightAttentionTitle`
  through `PatreonEndScreen`). Inferred.
- **MLP (chapter 7)**: `mlp.py` whole file (`LastTwoChapters` 8,
  `MLPStepsPreview` 230, `BasicMLPWalkThrough` 390,
  `NonlinearityOfLanguage` 1758, `Superposition` 1924, `MLPFeatures` 2202,
  `AlmostOrthogonal` 2625) plus `supplements.py` lines 1345-2212
  (`IntroducingMLPs`, `ReferenceFactStorage`, `WriteSuperposition`,
  `JohnsonLindenstraussName`, `ListOfFacts`) and the torch experiment in
  `almost_orthogonal.py`. Inferred.
- **LLMs explained briefly**: `chm.py` (inferred with high confidence from
  class names such as `PredictTheNextWord` 61, `ShowMachineWithDials` 896,
  `LargeInLargeLanguageModel` 1239, `WriteRLHF` 1414, `RLHFWorkers` 1452,
  `SerialProcessing` 1482, `ParallelProcessing` 1536, `TrainingDataCHM`
  1938, `ShowPreviousVideos` 2107 matching the article's RLHF, GPU and
  dial passages at `mini-llm/index.mdx` lines 21, 85, 120, 126-148) and
  `network_flow.py` `FlowForCHM` 1207, `FlowForCHM2` 1236. The expansion
  of "CHM" is unverified; the article does not mention it.
- **Cross-entropy and entropy (2026)**: `_2026/cross_entropy/`
  (`entropy.py`, `language_models.py`, `next_char.py`,
  `arithmetic_coding.py`, `robot.py` 8,801 lines, `transformer_render.py`
  with `TransformerModel` 104 and `TransformerForwardPass` 404). The split
  between Part 1 and Part 2 is unverified.

External data the code depends on (verified by reading):

- `_2017/nn/mnist_loader.py` line 42 opens an absolute path to
  `mnist.pkl.gz` on the author's machine; `_2017/nn/network.py` lines 28-29
  load the pretrained weights and `image_map` files that are present in the
  repository (309 KB, 324 KB, plus two alternates 679 KB and 577 KB).
- `_2024/transformers/helpers.py` lines 9-10 set `DATA_DIR` inside the
  Manim output directory (`2024/transformers/data/`, an `OWL3_Dictionary.txt`
  word list) which is not in the repository; `embedding.py` lines 1 and
  96-97 load a `gensim` word-vector model; `generation.py` lines 5-10 import
  Hugging Face `transformers` (GPT-2), `torch`, `openai` and `tiktoken`.
- `_2017/nn/part1.py` lines 10-14 emit a warning that the file uses the
  deprecated `ContinualAnimation`, and line 17 imports `nn.network` while
  `part2.py` line 7 imports `_2017.nn.network`, so the 2017 code is not
  runnable as-is even under ManimGL.

Consequence: the pipeline reads code; it does not render it. Rendering his
scenes is not an alignment option (section 4).

### Transcript sources

Options in order of preference:

1. **YouTube captions through yt-dlp.** `--write-subs` writes uploaded
   subtitles, `--write-auto-subs` writes automatic captions, `--sub-langs`
   selects languages, `--sub-format` sets the preferred format, and
   `--skip-download` fetches only metadata and subtitle files (yt-dlp README
   lines 775, 891-908, fetched 2026-10-25; see Sources). Whether the eight
   videos have uploader-provided English captions is **unverified**;
   `--list-subs` answers it. Uploaded captions are the gold transcript;
   automatic captions have word-level timing but ASR errors on math terms.
2. **Whisper on the downloaded audio.** `openai-whisper` 20250625 on PyPI
   (requires Python 3.8 or later); its README recommends the `turbo` model
   for English (an optimized `large-v3`, about 6 GB VRAM, README lines
   71-88). `faster-whisper` 1.2.1 runs the same models with CTranslate2 and
   int8 on CPU (README lines 7, 140); its CPU benchmark table (lines 42-52)
   shows the small model in minutes on CPU, so large models on this 4-CPU
   container would take hours for 149 minutes of audio (estimate). Exact
   CLI flag names for JSON output and word timestamps are **unverified**
   here; check `whisper --help` in the implementation session.
3. **Article text as a semantic key, never as the transcript.** It
   paraphrases and reorders; use it to label sections and to link figures.

### Keyframes

Two complementary sources:

- **Curated figures from the bucket** (section 2): 245 captioned frames for
  the eight videos, already keyed to article paragraphs. Download by
  listing each prefix and fetching the jpg objects (skip the png twins).
- **Scene-change frames from the video.** Download 1080p with yt-dlp, then
  extract with ffmpeg. Both of the following were verified on the local
  ffmpeg 6.1.1 build with a synthetic red-to-blue clip: the `select` filter
  expression `gt(scene,0.3)` passed exactly the frame at the cut
  (`showinfo` reported `pts_time:1`, and with `-fps_mode vfr` exactly one
  JPEG was written), and the `scdet` filter (threshold 0 to 100, default
  10) logged `lavfi.scd.score: 15.625, lavfi.scd.time: 1`.
  3Blue1Brown frames fade and morph rather than hard-cut, so expect to tune
  the threshold per video and to deduplicate near-identical frames by
  perceptual hash. PySceneDetect (`scenedetect` 0.7.2 on PyPI) is an
  alternative with content and adaptive detectors.

### Chapter markers

YouTube chapters come from timestamps in the description; yt-dlp exposes
them in `info.json` (`--write-info-json`, README line 697; `--embed-chapters`
and `--split-chapters` at lines 1006 and 1071 confirm that chapter data is
parsed). Whether these eight descriptions contain timestamps is
**unverified**. If absent, derive sections from article headings plus
figure positions, then refine with the transcript.

### Scene order

`stage_scenes.py` lines 11-30 (verified) return `SCENES_IN_ORDER` when a
module defines it and otherwise sort scene classes by their definition line
in the file. No file under `_2017/nn`, `_2024/transformers` or
`_2026/cross_entropy` defines `SCENES_IN_ORDER` (grep), so definition order
is the only machine-readable order, and the repository's `CLAUDE.md`
instructs "Organize scenes chronologically within files". Caveats: scenes
for one 2024 video span four or five files; `supplements.py` holds
interstitials for three videos in three consecutive blocks (inferred);
2017 files contain stubs and post-credit material; `Thumbnail`,
`EndScreen` and `PatreonThanks` classes are not narrated content.

### Thumbnail and metadata

`yt-dlp --write-thumbnail` (README line 745) and `--write-description`
(line 695) write the thumbnail and description; `info.json` carries title,
duration, upload date and chapters. The site builds its card image from the
same YouTube thumbnail URL pattern (`YouTube.tsx`, `getThumbnail`).

## 4. Aligning transcript sections to scene classes

### Signals and reliability

Reliability figures are estimates of the share of content scenes that each
signal places in the correct transcript section without human help.

- **Monotonic order.** Scene definition order maps monotonically to
  transcript time; solve it as a one-dimensional sequence alignment that
  uses the other signals as scores. Reliability: high (80-90 percent) for
  one-file videos (chapters 1 and 2); medium (about 60 percent) for 2024
  videos spread over several files. Evidence: `stage_scenes.py` lines
  11-30; the `CLAUDE.md` ordering rule.
- **Class-name matching.** Split CamelCase, stem, and match against
  transcript and article vocabulary by lexical overlap or sentence
  embeddings. Reliability: medium-high (60-75 percent), best for 2024 where
  names describe content. Evidence: `IntroduceSigmoid`, `IncludeBias`,
  `IntroduceWeightMatrix`, `QueryMap`, `ShowMasking`,
  `MultiHeadedAttention`.
- **String literals.** On-screen `Text`, `Tex` and `TexText` strings and
  pi-creature dialogue (`says`) matched against transcript and article.
  Reliability: high precision, moderate recall; the strongest automatic
  anchor. Evidence: `attention.py` strings such as "Attention Pattern",
  "Value matrix" and "Query/Key space"; `supplements.py` dialogue such as
  "Softmax!" and "This is a made-up motivating example"; `part3.py` line
  2085 "Essence of calculus".
- **Figure bridge.** Match video keyframes to bucket figures (the same
  frames; perceptual hash or CLIP), figures sit next to article paragraphs,
  and paragraphs match transcript sentences. Reliability: keyframe to
  figure high (about 85 percent); figure to paragraph exact; paragraph to
  transcript medium-high (about 75 percent). Evidence: the bucket inventory
  in section 2; 245 `<Figure>` tags.
- **On-screen text OCR.** OCR keyframes and match to `Tex` strings in code.
  Reliability: medium (50-60 percent) because of LaTeX versus OCR noise;
  most useful for equation-heavy 2017 scenes.
- **Render-and-compare.** Render his scenes and compare to keyframes. Not
  feasible: ManimGL plus missing data files and absolute paths (section 3).
- **Manual anchors.** A reader fixes three to six (time, class) pairs per
  video. Reliability: near 100 percent; cost about 30 minutes per video.

### Proposed alignment pipeline

1. Build the scene list per video from definition order, dropping helper
   mobjects, stubs, thumbnails and end screens, and tagging pi-creature
   scenes as interstitials.
2. Build the transcript with sentence timestamps (captions or Whisper) and
   split it into candidate sections at article headings, figure positions
   and long pauses.
3. Score every (scene, section) pair with string-literal hits, class-name
   similarity and figure-bridge hits; run a monotonic alignment (dynamic
   programming with a small penalty for skips, since not every scene
   survives the edit).
4. Emit records with a per-link confidence and the signals that fired.
5. Have a reader (human or agent with the video open) confirm or fix the
   low-confidence links and add anchors; re-run from step 3. Budget three
   to six anchors per video.
6. Store only paraphrased section summaries and time ranges, never verbatim
   transcript text, in the committed records (section 6).

### Alignment record schema

```json
{
  "video_id": "eMlx5fFNoYc",
  "lesson": "attention",
  "section_id": "s07",
  "t_start": 612.4,
  "t_end": 701.9,
  "transcript_summary": "paraphrase of what is narrated in this span",
  "article_heading": "heading or nearest figure name",
  "scene_classes": [
    {"file": "_2024/transformers/attention.py", "class": "QueryMap", "line": 1715}
  ],
  "anchors": [
    {"type": "string_literal", "value": "Query/Key space"},
    {"type": "figure", "object": "lessons/2024/attention/example.jpg"}
  ],
  "confidence": 0.8,
  "signals": ["order", "name_match", "string_literal"],
  "verified_by": "none"
}
```

## 5. Data volume

| Quantity | Estimate | Basis |
| ---------- | ---------- | ------- |
| Narrated minutes, primary tier | about 149 min | Third-party durations, section 1 |
| Narrated minutes, with secondary tier | add 40-70 min | Two 2026 videos, durations unverified |
| Transcript, plain text | 22-25 k words, 130-160 KB | 149 min at 150-170 words per minute |
| Transcript, timed (VTT or json3) | 0.5-1 MB | Timestamps multiply plain size 3-5 times |
| Whisper word-level JSON | 2-4 MB | Per-word records |
| Scene-change keyframes | 1,100-2,200 frames | One visual change every 4-8 s; consistent with 1,859 `self.play(` calls in the primary-tier files |
| Keyframes on disk, 1080p JPEG | 0.3-0.6 GB | 150-300 KB per frame |
| Keyframes downscaled to 480p for analysis | 50-90 MB | about 40 KB per frame |
| Bucket figures, jpg only | 100-130 MB | Half of 271.2 MB; png twins skipped |
| 1080p video downloads | 1.7-4.5 GB | 1.5-4 Mbps typical for animation content; unverified |
| Audio only (m4a or opus) | 150-250 MB | about 1-1.5 MB per minute |
| Source code | 2.3 MB `_2017/nn`, 0.7 MB `_2024/transformers`, 9.4 MB `_2026/cross_entropy` | `du -sh` |
| Articles | 189 KB MDX | Section 2 |

Container headroom: 30 GB free on `/`, 4 CPUs, 15 GB RAM (verified with
`df`, `nproc`, `free`), so downloads and keyframes fit locally; Whisper
`large-v3` on CPU is the only slow step.

### What to commit

Commit (original work, small, reproducible):

- Analysis records and alignment maps (JSON or Markdown) that contain
  paraphrased summaries, time ranges, class names, file paths and line
  numbers.
- A manifest of video IDs, expected durations, caption availability and
  content hashes of the downloaded files, so the corpus can be rebuilt.
- The download, transcription, keyframe and alignment scripts.
- The framework, rubric and pattern library with original ManimCE examples.

Do not commit (third-party copyrighted or bulky):

- Video, audio, keyframes or bucket figures.
- Verbatim transcripts or captions (store derived summaries only; keep raw
  transcripts in a gitignored cache).
- Article text from the site repository (all rights reserved).
- Any of his scene code (CC BY-NC-SA, and excluded by project decision).

Keep raw material under a gitignored `corpus/` directory with one folder per
video ID, and record its content hashes in the committed manifest.

## 6. Licensing and terms

- **`3b1b/videos` code**: CC BY-NC-SA 4.0 (`LICENSE.txt`; `README.md` states
  that Manim itself is MIT while this repository's contents are CC
  BY-NC-SA). Reading the code to derive principles is fine; copying scene
  code into the skill is excluded by project decision and would also pull
  the ShareAlike and NonCommercial terms onto the skill. Keep examples
  original and cite file and line when describing a technique.
- **`3b1b/3Blue1Brown.com` content**: all rights reserved, personal
  non-commercial evaluation permitted (`License.md`). Treat article text and
  bucket figures as private analysis inputs; do not redistribute, commit or
  bundle them; quote at most short fragments when a point cannot be made
  otherwise.
- **Bucket figures**: hosted by 3Blue1Brown LLC under the same terms; public
  readability is not a license. Fetch once, cache locally, do not mirror.
- **YouTube videos**: YouTube's Terms of Service forbid accessing,
  reproducing, downloading or distributing content except as the service
  authorizes or with permission from YouTube and the rights holders
  (**third-party**: wording summarized from WebSearch snippets of the terms
  page, which could not be fetched here). Downloading with yt-dlp for
  private analysis is therefore a terms-of-service risk even where copyright
  law would allow private study; the videos themselves are not covered by
  the code repository's CC license (**unverified** whether the channel
  applies any Creative Commons license to uploads). Mitigations: download
  only the eight primary videos, keep them local and gitignored, prefer
  captions and the bucket figures over frame extraction where they suffice,
  delete media after keyframes are extracted, never redistribute frames, and
  ship only original work in the skill.
- **Attribution**: whatever the skill ships, name 3Blue1Brown and link the
  two repositories as the sources of the derived principles, since
  CC BY-NC-SA requires attribution for derived material and the framework is
  derived from studying his work.

## 7. Unverified items and open questions

1. Exact durations of all videos (third-party, minute-rounded for eight;
   unknown for the 2026 pair, the talk and the guest video).
2. Whether uploader-provided English captions exist for each video
   (`yt-dlp --list-subs`).
3. Whether YouTube descriptions contain chapter timestamps.
4. Original YouTube titles (third-party snippets only).
5. The expansion of "CHM" in `chm.py` and the exact file-to-video split for
   the two 2026 videos.
6. The block boundaries inside `supplements.py` (inferred from names).
7. The 1080p bitrate and therefore download size.
8. Whisper CLI flag names for JSON output and word timestamps.
9. Whether the channel applies a Creative Commons license to its uploads.
10. Blocked hosts in this container (observed): youtube.com and its media
    hosts, 3blue1brown.com, docs.manim.community, 3b1b.github.io, and every
    third-party page WebFetch tried (DNS resolution failed through the
    proxy). Reachable: GitHub over git and raw.githubusercontent.com, PyPI,
    storage.googleapis.com. Plain `github.com` web pages answer HTTP 403
    through the proxy even though `git ls-remote` and `git clone` to the
    same repositories succeed, so the repository links in Sources could only
    be checked by git here; the raw, PyPI and bucket links all returned 200
    to `curl`.

## Appendix A: scene class inventory

Totals (verified): 2017 series 151 classes in three files (about 8 helper
mobjects, 40 pi-creature scenes, 8 external placeholders, 10 stubs, 6
thumbnails or end screens); 2024 series 255 scene classes across ten scene
files (two of them byte-identical duplicates), of which 39 are pi-creature
scenes and 5 are thumbnails or end screens, plus 10 helper classes in
`helpers.py`; 2026 directory 26 classes in the two files counted above, with
`robot.py`, `next_char.py`, `arithmetic_coding.py`, `distribution.py`,
`supplements.py`, `part2_supplements.py` and `transformer_render.py` not yet
counted.

Helper classes worth studying as reusable patterns (verified lines):
`NetworkMobject` (`part1.py` 94) and `MNistNetworkMobject` (262);
`NeuralNetwork` (`helpers.py` 342), `ContextAnimation` (396),
`WeightMatrix` (471), `NumericEmbedding` (524), `EmbeddingArray` (568),
`RandomizeMatrixEntries` (630), `Dial` (655), `MachineWithDials` (761);
`LanguageModel` (`language_models.py` 40); `TransformerModel`
(`transformer_render.py` 104).

## Appendix B: pipeline commands

Flags below are cited from the yt-dlp README fetched on 2026-10-25 (lines
695-1071 and the format-selection section around line 1662) and could not
be run here; the ffmpeg commands were run locally on a synthetic clip.
Confirm the yt-dlp commands in the implementation session.

```bash
# Metadata, description, thumbnail and captions only (no media)
yt-dlp --skip-download --write-info-json --write-description \
  --write-thumbnail --write-subs --write-auto-subs \
  --sub-langs "en.*" --sub-format "json3/vtt" \
  -o "corpus/raw/%(id)s/%(id)s.%(ext)s" VIDEO_ID

# List available caption tracks before deciding on Whisper
yt-dlp --list-subs VIDEO_ID

# Best video up to 1080p plus best audio (format strings per the README)
yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" \
  -o "corpus/raw/%(id)s/%(id)s.%(ext)s" VIDEO_ID

# Scene-change keyframes; select, showinfo and -fps_mode vfr verified locally
mkdir -p corpus/frames/VIDEO_ID
ffmpeg -i corpus/raw/VIDEO_ID/VIDEO_ID.mp4 \
  -vf "select='gt(scene,0.3)',showinfo" -fps_mode vfr \
  corpus/frames/VIDEO_ID/%05d.jpg 2> corpus/frames/VIDEO_ID/showinfo.log

# Alternative detector with a numeric score per cut (default threshold 10)
ffmpeg -i corpus/raw/VIDEO_ID/VIDEO_ID.mp4 -vf "scdet=threshold=10" \
  -f null - 2> corpus/frames/VIDEO_ID/scdet.log
```

```bash
# Enumerate and fetch the curated figures of one lesson (public bucket)
BUCKET="https://storage.googleapis.com/3blue1brown-website-bucket"
curl -sS "$BUCKET?prefix=lessons/2024/attention/&max-keys=1000" \
  | grep -o '<Key>[^<]*\.jpg</Key>' | sed 's/<[^>]*>//g' \
  | while read -r key; do
      mkdir -p "corpus/figures/$(dirname "$key")"
      curl -sS -o "corpus/figures/$key" "$BUCKET/$key"
    done
```

## Sources

Fetched or read for this map:

- 3b1b `videos` repository: <https://github.com/3b1b/videos> (local clone at
  `/home/user/3b1b/videos`; files and lines cited inline).
- 3b1b site repository: <https://github.com/3b1b/3Blue1Brown.com> (sparse
  clone at `/home/user/3b1b/3Blue1Brown.com`).
- Site asset bucket: <https://storage.googleapis.com/3blue1brown-website-bucket>
  (object GET and XML listing observed on 2026-10-25).
- yt-dlp README (flag names and line numbers):
  <https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/README.md>;
  project page <https://github.com/yt-dlp/yt-dlp>; PyPI release 2026.10.21
  <https://pypi.org/project/yt-dlp/>.
- openai-whisper README:
  <https://raw.githubusercontent.com/openai/whisper/main/README.md>; project
  <https://github.com/openai/whisper>; PyPI release 20250625
  <https://pypi.org/project/openai-whisper/>.
- faster-whisper README:
  <https://raw.githubusercontent.com/SYSTRAN/faster-whisper/master/README.md>;
  project <https://github.com/SYSTRAN/faster-whisper>; PyPI release 1.2.1
  <https://pypi.org/project/faster-whisper/>.
- PySceneDetect: PyPI release 0.7.2 <https://pypi.org/project/scenedetect/>.
- ManimCE: PyPI release 0.22.0 <https://pypi.org/project/manim/> (requires
  Python 3.11 or later).
- Local tools: ffmpeg and ffprobe 6.1.1, Python 3.13.17.

Third-party facts (durations, original YouTube titles, YouTube terms wording)
came from WebSearch result snippets whose pages could not be opened from
this container and are therefore not linked.
