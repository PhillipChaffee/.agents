# Map of the 2024 Transformer Series Source (ManimGL)

This document maps the Manim source for the 3Blue1Brown transformer series
(deep-learning chapters 5 to 7, plus the Computer History Museum talk) as it
exists in the `3b1b/videos` repository, directory `_2024/transformers/`. It is
the sibling of the 2017 neural-network map and follows the same section
structure, then adds two sections the brief asked for: the 2017 to 2024
evolution visible in this code, and the external data the scenes depend on.

Every claim below is tied to a `file:line` reference into the read-only clone at
`/home/user/3b1b/videos` (commit `306a1346a356c7a7b097875ceb51c5cd67d0a56c`,
dated 2026-09-29, remote <https://github.com/3b1b/videos>). Where a claim
concerns the animation library rather than the scenes, it cites the ManimGL
source cloned to `/home/user/3b1b/manim` (commit
`fafa083a4fb274bba9cabde0b6e2f50ba6da0622`, <https://github.com/3b1b/manim>)
or the ManimCE source cloned to `/home/user/ManimCommunity/manim` (commit
`bb380986b16273d4197bcf21e1365b5f0dcad505`, version 0.22.0,
<https://github.com/ManimCommunity/manim>). Anything not verified against one
of those three trees is marked **unverified**.

The repository is licensed CC BY-NC-SA 4.0 (`/home/user/3b1b/videos/LICENSE`,
line 1). This map describes structure and technique; it quotes no scene code
beyond the short identifiers needed to locate things.

## Reading coverage and method

| File | Lines | Lines read | Coverage | Notes |
| --- | ---: | ---: | ---: | --- |
| `helpers.py` | 819 | 819 | 100% | Shared mobjects and animations |
| `supplements.py` | 2252 | 2252 | 100% | Pi-creature reaction shots and inserts |
| `embedding.py` | 3047 | 3047 | 100% | Chapter 5 embeddings, chapter 6 and 7 inserts |
| `attention.py` | 4093 | 4093 | 100% | Chapter 6 |
| `network_flow.py` | 1531 | 1531 | 100% | 3D "flow through the network" scenes |
| `generation.py` | 986 | 986 | 100% | Autoregressive sampling with real models |
| `mlp.py` | 2627 | 2585 | 98% | Chapter 7 (lines 2257 to 2298 skipped) |
| `chm.py` | 2160 | 1640 | 76% | CHM talk (700 to 880 and 1350 to 1482 skipped) |
| `ml_basics.py` | 2430 | 1810 | 74% | Chapter 5 ML premise and softmax (1330 to 1814 skipped) |
| `auto_regression.py` | 599 | 599 | 100% | Byte-identical to `old_auto_regression.py` |
| `old_auto_regression.py` | 599 | 0 | dup | `diff` reports identical to `auto_regression.py` |
| `almost_orthogonal.py` | 51 | 51 | 100% | Standalone PyTorch script, not a scene file |
| `_2026/cross_entropy/transformer_render.py` | 423 | 423 | 100% | Most recent example, read in full |

Method: `grep -n '^class '` on every file for the inventory, full reads of the
files above, then `grep -c` counts across the ten unique scene files
(`old_auto_regression.py` excluded as a duplicate) for the idiom table. Counts
are "lines containing the pattern", not call occurrences.

The user's note asked for a tool called "Ultracode". The kit's
`CHANGELOG.md` line 58 records that an `ultracode` skill was removed in a
previous release, and nothing by that name exists under
`/home/user/.agents/skills`, so this map was produced by direct reading.

## 1. Scene inventory

### 1.1 How the files map onto videos

The series code is organized by topic, not by video, and the three chapters
draw on overlapping files. The grouping below follows the section comments in
the files themselves (`supplements.py:6` "Intro chapter", `:838` "Attention
chapter", `:1342` "MLP Chapter"; `embedding.py:116` "For chapter 5", `:2230`
"For chapter 6", `:2569` "For chapter 7").

| Video | Main files | Representative scenes |
| --- | --- | --- |
| Chapter 5: But what is a GPT? | `ml_basics.py`, `generation.py`, `embedding.py`, `network_flow.py`, `supplements.py` (9 to 835) | `PremiseOfML`, `SimpleAutogregression`, `IntroduceEmbeddingMatrix`, `KingQueenExample`, `HighLevelNetworkFlow`, `SoftmaxBreakdown` |
| Chapter 6: Attention in transformers | `attention.py`, `embedding.py` (2232 to 2566), `supplements.py` (841 to 1339) | `AttentionPatterns`, `QueryMap`, `IntroduceValueMatrix`, `CountMatrixParameters`, `MultiHeadedAttention` |
| Chapter 7: How might LLMs store facts | `mlp.py`, `embedding.py` (2571 to 3047), `supplements.py` (1345 to 2252) | `BasicMLPWalkThrough`, `NonlinearityOfLanguage`, `Superposition`, `MJSpace` |
| CHM talk | `chm.py` (reuses everything above via star imports at `chm.py:1-5`) | `PredictTheNextWord`, `ShowMachineWithDials`, `FirthQuote`, `ManyComputationsPerUnitTimeV2` |

### 1.2 Class inventory with line numbers

`helpers.py` (10 classes, no scenes):

- `NeuralNetwork(VGroup)` 342, `ContextAnimation(LaggedStart)` 396,
  `LabeledArrow(Arrow)` 445, `WeightMatrix(DecimalMatrix)` 471,
  `NumericEmbedding(WeightMatrix)` 524, `EmbeddingArray(VGroup)` 568,
  `RandomizeMatrixEntries(Animation)` 630, `AbstractEmbeddingSequence` 651
  (empty stub), `Dial(VGroup)` 655, `MachineWithDials(VGroup)` 761.

`embedding.py` (30 scenes):

- Chapter 5: `LyingAboutTokens2` 119, `DiscussTokenization` 260 (empty),
  `ImageTokens` 265, `SoundTokens` 299, `IntroduceEmbeddingMatrix` 341,
  `Word2VecScene` 612 (base), `AmbientWordEmbedding` 696,
  `ThreeDSpaceExample` 778, `HighDimensionalSpaceCompanion` 906,
  `LearningEmbeddings` 1019, `KingQueenExample` 1107,
  `HitlerMussoliniExample` 1385, `SushiBratwurstExample` 1495,
  `SizeDirection` 1511, `PluralityDirection` 1569, `ShowNearestNeighbors` 1601
  plus four one-line subclasses 1694 to 1710, `DotProducts` 1724,
  `DotProductWithPluralDirection` 1885, `DotProductWithGenderDirection` 2067,
  `RicherEmbedding` 2081.
- Chapter 6: `MultipleMoleEmbeddings` 2232, `RefineTowerMeaning` 2365,
  `UpdatingPoetryEmbedding` 2470.
- Chapter 7: `SimpleSpaceExample` 2571, `ManyIdeasManyDirections` 2695,
  `MJSpace` 2758.

`attention.py` (20 scenes):

- `AttentionPatterns` 10 (the chapter's spine, 1443 lines to 1452 including
  two never-called scratch methods at 1362 and 1385), `MyseteryNovel` 1453
  (sic), `RoadNotTaken` 1548, `QueryMap` 1715, `KeyMap` 1839,
  `DescribeAttentionEquation` 1850, `ShowAllPossibleNextTokenPredictions` 2083,
  `ShowMasking` 2169, `ScalingAPattern` 2259, `IntroduceValueMatrix` 2313,
  `CountMatrixParameters` 2561, `LowRankTransformation` 3014,
  `ThinkAboutOverallMap` 3104, `CrossAttention` 3120, `CarCrashedExample` 3304,
  `TwoHarrysExample` 3329, `ManyTypesOfUpdates` 3361, `MultiHeadedAttention`
  3503, `OutputMatrix` 3897, `Parallelizability` 4036.

`mlp.py` (16 scenes):

- `LastTwoChapters` 8, `AltLastTwoChapters` 182, `MLPIcon` 214,
  `MLPStepsPreview` 230, `MatricesVsIntuition` 377 (stub),
  `BasicMLPWalkThrough` 390 (1368 lines to 1757), `NonlinearityOfLanguage`
  1758, `Superposition` 1924, `StackOfVectors` 2136, `ShowAngleRange` 2183,
  `MLPFeatures` 2202, `BreakDownThreeSteps` 2299, `SuperpositionVectorBundle`
  2445, `ClassicNeuralNetworksPicture` 2515 (stub),
  `ShowBiasBakedIntoWeightMatrix` 2520, `AlmostOrthogonal` 2625 (stub; the
  real computation is the script `almost_orthogonal.py`).

`network_flow.py` (14 scenes):

- `HighLevelNetworkFlow` 7 (base, 658 lines), `SimplifiedFlow` 668,
  `AltIntro` 700, `SimplifiedFlowAlternateAngle` 707,
  `LongerFlowLongerAttention` 715, `MentionContextSizeAndUnembedding` 723,
  `FlowForMLPIntroReview` 1176, `FlowForCHM` 1207, `FlowForCHM2` 1236,
  `TextToNumerical` 1253, `FlowForCHMNoText` 1262, `TextPassageIntro` 1268,
  `ThumbnailBase` 1341, `MoleExample1` 1371.

`generation.py` (24 scenes, 4 module functions):

- Functions: `get_gpt2_tokenizer` 14, `get_gpt2_model` 19,
  `gpt2_predict_next_token` 23, `gpt3_predict_next_token` 46, `clean_text`
  66, `next_token_bar_chart` 70.
- `SimpleAutogregression` 112 (base, sic), `AltSimpleAutoRegression` 399,
  `AnnotateNextWord` 412, `QuickerRegression` 456, `AutoregressionGPT3` 460,
  `QuickRegressionGPT3` 464, `GPT3CleverestAutocomplete` 469,
  `GPT3OnLearningSimpler` 483, `GPT3OnLongPassages` 534,
  `GPT3CreaturePrediction` 540, `GPT3CreaturePrediction2` 545,
  `LowTempExample` 550, `HighTempExample` 571, `MidTempExample` 576,
  `ChatBotPrompt` 582, `ChatBotPrompt2` 672, `ChatBotPrompt3` 676,
  `VoiceToTextExample` 680, `TextToVoiceExample` 744, `TextToImage` 760,
  `TranslationExample` 814, `PredictionVsGeneration` 824,
  `ManyParallelPredictions` 875, `PeekUnderTheHood` 953.

`ml_basics.py` (14 scenes):

- `DialTest` 7, `MLWithinDeepL` 20, `ShowCross` 298, `FlashThroughImageData`
  307, `FlashThroughTextData2` 330, `TweakedMachine` 359, `PremiseOfML` 392
  (580 lines), `PremiseOfMLWithText` 975, `PremiseOfMLWithMatrices` 1029,
  `LinearRegression` 1036, `ShowGPT3Numbers` 1174, `DistinguishWeightsAndData`
  1666, `SoftmaxBreakdown` 1814 (551 lines), `CostFunction` 2368.

`chm.py` (38 scenes): three `TeacherStudentsScene` openers (10, 32, 45);
"Version 1" (`chm.py:59`) `PredictTheNextWord` 61, `LotsOfTextIntoTheMachine`
185, `EvenMoreTextIntoMachine` 232, `WriteTransformer` 251, `LabelVector` 258,
`AdjustingTheMachine` 272, `FirthQuote` 303, `DownByTheRiverHeader` 445,
`RiverBankProbParts` 455, `FourStepsWithParameters` 486, `ChatbotFeedback`
549, `ContrastWithEarlierFrame` 622, `SequentialProcessing` 650; "Version 2"
(`chm.py:685`) `PartialScript` 688, `ShowMachineWithDials` 896,
`ShowSingleTrainingExample` 1111, `ParameterWeight` 1220,
`LargeInLargeLanguageModel` 1239, `ThousandsOfWords` 1257,
`EnormousAmountOfTrainingText` 1273, `BadChatBot` 1350, `WriteRLHF` 1414,
`RLHFWorker` 1433, `RLHFWorkers` 1452, `SerialProcessing` 1482,
`ParallelProcessing` 1536, `ManyComputationsPerUnitTimeV2` 1577,
`VectorLabel` 1810, `ParameterToVectorAnnotation` 1830, `ThreeWordsToOne`
1855, `ExamplePhraseHeader` 1921, `TrainingDataCHM` 1938, `DivyUpParameters`
2004, `ShowPreviousVideos` 2107, `EndScreen` 2156.

`supplements.py` (79 scenes, 35 of them `TeacherStudentsScene` subclasses):
mostly 10 to 40 line reaction shots such as `SkipAhead` 522, `Outdated` 573,
`ShoutSoftmax` 1024, `CalledMasking` 1059, `NowRepeatManyTimes` 1229,
`ThatsIt` 1792, `AskIfThisIsReal` 1917; plus graphic inserts such as
`GPTInitials` 9, `GamePlan` 330, `NetworkEndAnnotation` 730,
`HighlightAttentionTitle` 841, `OneThirdOfWhatYouNeed` 1282,
`MovingToSecondToken` 1604, `ReflectOnTwoThings` 1825,
`SingleNeuronVsMultiple` 1941, `DetailsNotDiscussed` 2124, `ListOfFacts` 2212.

`auto_regression.py` (10 scenes): an earlier revision of `generation.py`.
`diff` of the first 400 lines against `generation.py` shows 106 changed lines
(the newer file adds `clean_text`, `next_token_bar_chart`, and reorders the
top-k selection at `generation.py:61-63`). Unique to the old file:
`ModelTakingInTextWithSurroundingPieces` 450 (empty), `AthleteCompletion` 455,
`ThatWhichDoesNotKillMe` 584.

### 1.3 Structural observations

1. One base scene, many thin subclasses. `SimpleAutogregression` carries all
   logic and 23 subclasses change only class attributes (`seed_text`,
   `model`, `n_predictions`, `skip_through`), for example
   `generation.py:456-467`. `HighLevelNetworkFlow` is reused the same way
   (`network_flow.py:668-720`, `1176-1266`). `Word2VecScene` is the base for
   13 embedding scenes.
2. Scenes are long linear scripts. `AttentionPatterns` runs 1443 lines with
   46 section-beat comments; `BasicMLPWalkThrough` runs 1368 lines. By
   contrast the pi-creature cutaways in `supplements.py` average 28 lines.
3. Scratch is left in place: `scrap()` and `thumbnail()` methods that are never
   called (`attention.py:1362`, `1385`, `2900`), a `return` followed by
   "#### Trash ####" (`mlp.py:2432-2433`), an `if False:` block
   (`network_flow.py:327`), and a "# Temporary" block (`network_flow.py:62-81`).
4. Rendering is resumed mid-scene: "(Start re-rendering here, 151)" at
   `attention.py:1140` and "# Skip to animation 9" at `ml_basics.py:1030`.
5. Every scene is an `InteractiveScene` (122 matching lines) or a pi-creature
   subclass of it (`custom/characters/pi_creature_scene.py:37`, `:255`), which
   is ManimGL's live-window scene with mouse selection and an embedded IPython
   shell (`/home/user/3b1b/manim/manimlib/scene/interactive_scene.py:60-80`).

## 2. Visual abstractions

These are the recurring on-screen "nouns". Each is built by a helper so it
looks identical across scenes.

### 2.1 Token rectangles

A sentence is a `Text`, split into word or token sub-mobjects by
`break_into_words` / `break_into_tokens` (`embedding.py:41-50`), which call
`tiktoken.encoding_for_model("davinci")` (`embedding.py:9-10`) and map byte
offsets back to glyphs with `substr_to_path_count` (`embedding.py:35-36`).
`get_piece_rectangles` (`embedding.py:53-90`) draws a translucent rectangle
behind each piece: fill opacity 0.15, stroke width 1, a random bright color
per piece from `hue_range=(0.5, 0.6)` (blue-teal), and a `leading_spaces`
flag that makes rectangles abut so the whole line reads as a tape of tokens
(`network_flow.py:170-173`). The last token is replaced by a yellow box and
"???" (`embedding.py:127-130`, `network_flow.py:175-178`).

### 2.2 Numeric vectors and weight matrices

`WeightMatrix` (`helpers.py:471-521`) is a `DecimalMatrix` of random values in
(-9.9, 9.9) with one decimal, a sign, and an ellipsis row and column at index
-2, colored by `value_to_color` (`helpers.py:51-65`): positive values run
`BLUE_E` to `BLUE_B`, negatives `RED_E` to `RED_B`, interpolated in HSL by
magnitude. `NumericEmbedding` (`helpers.py:524-565`) is the same object as a
column with a grey-to-white ramp instead, so data vectors read as neutral and
weights read as colored. `EmbeddingArray` (`helpers.py:568-627`) is a row of
`NumericEmbedding`s inside one tall bracket with a `\dots` substituted for one
column. `RandomizeMatrixEntries` (`helpers.py:630-648`) animates every entry
to a new random value and recolors; it is the visual for "the weights
changed" and appears in 15 lines across the series.

### 2.3 Collapsed symbols

Once a vector has been shown numerically, it is collapsed into a symbol:
`Tex(R"\vec{\textbf{E}}_{0}")` with `make_number_changeable` to stamp the
subscript (`attention.py:166-175`). The collapse is animated by fading each
entry into the symbol while the brackets squash to zero height
(`attention.py:200-221`). The same template produces `Q`, `K`, `V` symbols in
the role colors (`attention.py:435-444`, `549-552`, `1037-1040`) and `W_Q`,
`W_K`, `W_V` matrix labels (`attention.py:404`, `564`, `1029`). Chapter 7
collapses whole products into `W_\uparrow \vec{E}_i + \vec{B}_\uparrow`
(`mlp.py:1048-1051`).

### 2.4 The machine with dials

A model is a grey box (`GREY_D`) full of small dials (`MachineWithDials`,
`helpers.py:761-819`). Each `Dial` (`helpers.py:655-758`) is a 270 degree arc
with ticks and a needle whose color follows `value_to_color`;
`animate_set_value` sweeps the needle and throws `VShowPassingFlash` streaks
along concentric arcs (`helpers.py:725-754`). "Training" is
`random_change_animation` (`helpers.py:800-808`), used in loops of 50 examples
(`ml_basics.py:462-474`) and on 9 by 9 grids of tiny machines
(`chm.py:1273-1319`).

### 2.5 The transformer as a stack of slabs

In `generation.py:174-207` the transformer is ten `VPrism(3, 2, 0.2)` slabs
arranged along `OUT`, tilted by `machine_phi` and `machine_theta`, with the
label on the front slab. Input text flies into the stack while slabs flash
`TEAL` in sequence (`generation.py:253-275`). `network_flow.py:129-160` uses a
`Cube` per block with `set_shading(0.5, 0.5, 0.0)` and a 96 point title, and
`mlp.py:403-409` a `VCube` with the front face hidden so the camera can look
inside.

### 2.6 Attention grid

Queries along the top, keys down the side, grid lines, then a dot in each
cell whose diameter encodes the softmax weight (`attention.py:665-735`;
`ScalingAPattern` builds a 50 by 50 version at `attention.py:2263-2282`).
Masked cells get a red square and shrink to nothing (`attention.py:983-1004`).
`ShowMasking` shows the numeric version with `-\infty` in red
(`attention.py:2213-2256`).

### 2.7 Embedding space

`Word2VecScene` (`embedding.py:612-693`) loads GloVe vectors through gensim,
projects them onto three principal components (`embedding.py:13-19`) and
draws `LabeledArrow`s in `ThreeDAxes`. Arrows call
`always.set_perpendicular_to_camera(self.frame)` so they stay legible while
the camera orbits (`embedding.py:692`). Later chapters replace real GloVe
coordinates with hand-chosen ones that preserve the story
(`attention.py:2365-2367`, `embedding.py:2282-2288`, `2814-2817`).

### 2.8 Context arcs

`ContextAnimation` (`helpers.py:396-442`) draws arcs from many source words to
one target and runs `VShowPassingFlash` along each with random lag; arcs are
colored from `hue_range=(0.1, 0.3)` (yellow-green) and widths follow random
"strengths" squared. It is the universal visual for "this word absorbs
context" (17 lines across the series; `network_flow.py:356-385` builds a
per-layer variant by hand).

### 2.9 Next-token bar chart

`get_distribution` (`generation.py:209-242`) lays out horizontal bars with a
`TEAL` to `YELLOW` gradient, word labels on the left, integer percentages on
the right, and a `\vdots`. Sampling is shown by a yellow highlight rectangle
jumping between bars under a seeded random choice (`generation.py:291-311`).

### 2.10 Dots-and-lines network icon

`NeuralNetwork` (`helpers.py:342-393`) and `get_network_connections`
(`helpers.py:313-323`): dots with random fill opacity, lines colored by
`value_to_color` and width by a random power. It appears as a small icon
(`mlp.py:145-171`) and as a 3D `DotCloud` of neurons inside the MLP block
(`network_flow.py:420-427`, `mlp.py:1661-1673`).

### 2.11 Other recurring devices

- "Data" words flying across a matrix while entries randomize
  (`data_modifying_matrix`, `helpers.py:240-292`; 10 call sites) stands for
  "learned from data".
- A wobbling thought-bubble blob stands for an N-dimensional space
  (`embedding.py:921-942`, `mlp.py:2114-2133`).
- A dodecahedron's face centers give "many nearly perpendicular vectors"
  (`supplements.py:1889-1902`, `mlp.py:2093-2101`).
- A `BarChart` turned sideways becomes the unembedding output
  (`network_flow.py:616-636`).

## 3. Color system

### 3.1 Semantic assignments (with evidence)

| Meaning | Color | Evidence |
| --- | --- | --- |
| Query | `YELLOW` | `attention.py:370`, `437`, `1870`; `QueryMap.map_color` 1717 |
| Key | `TEAL` | `attention.py:551`, `565`, `1870`; `KeyMap.map_color` 1841 |
| Value | `RED` | `attention.py:1028`, `2037-2041`, `2423` |
| Value down / up factors | `RED_C` / `RED_B` | `attention.py:3366`, `3935-3936` |
| Output matrix | `PINK` | `attention.py:3999-4001` |
| Embedding symbol | `GREY_A` | `attention.py:174`, `3176` |
| Weights, positive and negative | `BLUE_E..BLUE_B` / `RED_E..RED_B` | `helpers.py:51-65`, `482-485` |
| Data vectors | `GREY_C..WHITE` | `helpers.py:536-537` |
| Token rectangles | random hue 0.5 to 0.6 | `embedding.py:61`, `70` |
| Context arcs | random hue 0.1 to 0.3 | `helpers.py:402`, `network_flow.py:366` |
| Highlight box | `YELLOW` stroke 2 or 3 | `network_flow.py:612-613`, `generation.py:297` |
| Seed text / user prompt | `BLUE_B` / `BLUE` | `generation.py:118`, `648-649` |
| System prompt | `GREEN` | `generation.py:626-630` |
| Wrong, masked, warning | `RED` | `attention.py:2219-2221`, `chm.py:1180-1185`, `supplements.py:1381` |
| Correct | `GREEN` | `supplements.py:802`, `1390`, `2005` |
| Linear map labels in MLP | `BLUE`, bias `BLUE_B` | `mlp.py:1051`, `1538-1539` |
| First name / last name / basketball features | `YELLOW` / `RED` / `#F88158` | `mlp.py:1777-1778`, `1472`, `embedding.py:2813` |
| Scene background | `#000000` | `custom_config.yml:21` |
| Pi-creature backdrop | `GREY_E` | `custom/characters/pi_creature_scene.py:258` |
| Students / teacher | `BLUE_D, BLUE_E, BLUE_C` / `GREY_BROWN` | `pi_creature_scene.py:256-257` |

### 3.2 Token counts (lines containing the token, ten unique files)

`YELLOW` 138, `WHITE` 103, `BLUE` 91, `RED` 72, `BLACK` 63, `TEAL` 61,
`GREY_B` 45, `GREY_A` 20, `GREEN` 20, `RED_B` 19, `GREY_C` 17, `BLUE_B` 17,
`PINK` 15, `GREY` 12, `GREY_D` 11, `BLUE_D` 9, `GREY_E` 7, `BLUE_E` 6,
`ORANGE` 4; every other shade appears three times or fewer. Hex literals are
rare (13 total) and are brand or flag colors: `#F88158` (basketball orange,
`supplements.py:1755`), `#CE1141` (Chicago Bulls), `#008C45` and `#FFCC00`
(Italy and Germany, `embedding.py:1387`), `#BC002D` (Japan, `1497`), the three
CHM logo blues (`chm.py:1869`), and two off-white backgrounds for the paper
script and the layer wrapper (`chm.py:884`, `mlp.py:2569`).

### 3.3 Rules that fall out of the counts

1. The palette is a handful of saturated hues on black, with grey levels doing
   most of the de-emphasis work (`set_opacity(0.25)` or `fade(0.5)` appear in
   149 and 30 lines respectively).
2. Each mathematical role owns one hue for the whole chapter; the hue is
   introduced on the first appearance and reused in every later symbol,
   matrix label and brace.
3. Randomness is constrained to a narrow hue band (`random_bright_color(hue_range=...)`,
   13 lines; the ranges are listed in the counts table) so crowds of objects
   look varied but related.
4. `set_backstroke(BLACK, n)` (40 lines) outlines text that sits over
   graphics, for example titles over 3D blocks (`network_flow.py:152`).
5. Text that must read as "this is real output" is colored by truth: the
   sampled token turns `YELLOW` (`generation.py:513`), a bad prediction gets a
   red arrow (`chm.py:1181-1185`).

## 4. Layout and camera

### 4.1 2D layout grammar

- Everything is placed relative to other objects: `next_to`, `to_edge`,
  `to_corner`, `arrange`, `arrange_in_grid`, `match_x`, `match_y`,
  `align_to`. Absolute coordinates are used only to pin overlays onto
  pre-rendered stills (`supplements.py:739-742`, `847-848`,
  `attention.py:1859-1860`).
- Width budgets are expressed in frame units: `set_max_width(FRAME_WIDTH - 1)`
  (`network_flow.py:165`), thirds at `FRAME_WIDTH / 3` (`supplements.py:79`,
  `network_flow.py:1440-1445`), halves at `FRAME_WIDTH / 4`
  (`supplements.py:694`, `769-770`).
- Split screens use a full-height `Line` and two titles
  (`supplements.py:686-709`, `765-784`, `chm.py:622-647`).
- Content meant to sit beside a video inset uses `ScreenRectangle`
  (`supplements.py:398-403`, `1112-1117`, `attention.py:3514-3517`).
- `TeacherStudentsScene` fixes a layout: three students bottom-left, teacher
  bottom-right, a black 4-unit `ScreenRectangle` in the top-left corner and a
  `hold_up_spot` above the teacher's left shoulder
  (`pi_creature_scene.py:255-298`).

### 4.2 3D layout grammar

- `self.set_floor_plane("xz")` (18 lines) switches the camera's Euler axes so
  that `OUT` becomes the depth of the network
  (`/home/user/3b1b/manim/manimlib/scene/scene.py:725-731`). Layers are then
  stacked along `OUT` with `next_to(layer, OUT, buff=...)`
  (`network_flow.py:148`, `417`).
- The camera is driven by `frame.reorient(theta, phi, gamma, center, height)`
  whose arguments are degrees, a 3-tuple and a frame height
  (`manimlib/camera/camera_frame.py:178-194`). The scenes contain 139 lines
  with `reorient(`, 110 of them `frame.animate.reorient(...)` inside a
  `self.play`. The literals have the look of values copied from the
  interactive window, for example `(-57, -8, 0, (-6.59, 1.2, 57.84), 30)`
  at `network_flow.py:569`.
- Slow ambient motion: `frame.add_ambient_rotation(k * DEGREES)` (12 lines;
  defined at `camera_frame.py:218-220`) or a custom theta updater
  (`chm.py:297`, `embedding.py:1404`).
- HUD elements are pinned with `fix_in_frame()` (50 lines;
  `manimlib/mobject/mobject.py:1894-1896`): equations in the corner
  (`embedding.py:1342`), word lists (`network_flow.py:879`), titles
  (`attention.py:3558`). `IntroduceValueMatrix` overrides `add` so that a
  flag decides whether new mobjects are fixed (`attention.py:2554-2558`).
- Lighting and depth: `self.camera.light_source.move_to([-10, 10, 15])` and a
  light that follows the frame's z (`network_flow.py:43-44`),
  `apply_depth_test()` on lines and vectors (`network_flow.py:466`,
  `embedding.py:1428`), `deactivate_depth_test()` plus manual `sort` on cubes
  (`network_flow.py:144-149`), `set_flat_stroke(False)` for lines meant to
  have 3D thickness (`embedding.py:806`, `network_flow.py:467`).
- Field of view is narrowed for near-orthographic shots:
  `set_field_of_view(20 * DEGREES)` (`generation.py:176`), `30 * DEGREES`
  (`mlp.py:414`, `attention.py:1744`), `10 * DEGREES` (`attention.py:3018`).

### 4.3 The camera as a narrative device

- Zoom-to-detail: `frame.animate.set_height(11).move_to(...)` to make room
  for a count (`embedding.py:603`), then `frame.animate.to_default_state()`
  to return (`mlp.py:535`, `chm.py:107`).
- Orbit while something is contemplated: 8 to 12 second
  `frame.animate.reorient` with nothing else moving (`network_flow.py:662-665`,
  `embedding.py:1202-1205`, `mlp.py:531-532`).
- A continuous growth updater on the frame height makes a repeated process
  feel like it recedes: `frame.add_updater(lambda f: f.set_height(... + rate * t))`
  (`network_flow.py:685-687`) and exponential growth for "enormous data"
  (`chm.py:1293`).
- The frame scrolls a long document: `frame.animate.set_y(-15.4)` over 5
  seconds through a mystery story (`attention.py:1488-1494`) and a 30 second
  pan down nested timelines (`chm.py:1667-1684`).

## 5. Animation idioms with counts

### 5.1 Count table (lines containing the pattern, ten unique scene files)

| Idiom | Count | Typical use and evidence |
| --- | ---: | --- |
| `self.play(` | 1083 | |
| `self.wait(` | 705 | 542 are bare `wait()` |
| `FadeIn(` | 369 | often with `shift=` or `scale=` and `lag_ratio` |
| `FadeOut(` | 300 | often with a direction, e.g. `FadeOut(x, DOWN)` |
| `LaggedStartMap(` | 201 | staggered mapping over a group |
| `LaggedStart(` | 192 | staggered list of heterogeneous animations |
| `Transform(` | 158 | includes `.animate` usage via substring |
| `TransformFromCopy(` | 148 | "this gives rise to that" while source stays |
| `ShowCreation(` | 127 | lines, rectangles, arrows |
| `SurroundingRectangle(` | 126 | highlight box |
| `Write(` | 117 | text and small diagrams |
| `generate_target(` | 96 | plan a layout, then `MoveToTarget` |
| `FadeTransform(` | 85 | one text becomes another |
| `time_span=` | 85 | stagger sub-animations within one `play` |
| `MoveToTarget(` | 81 | |
| `path_arc=` | 58 | curved motion and curved arrows |
| `save_state(` | 52 | with 34 `Restore(` |
| `set_anim_args(` | 51 | run_time or rate_func on `.animate` chains |
| `GrowArrow(` | 50 | |
| `Brace(` | 49 | dimension and count callouts |
| `GrowFromCenter(` | 44 | braces, arrows |
| `set_backstroke(` | 40 | outline text over graphics |
| `ReplacementTransform(` | 32 | |
| `rate_func=` | 31 | `there_and_back` 18, `linear`, `rush_from`, `wiggle` |
| `FadeInFromPoint(` | 25 | "emerges from here" |
| `add_updater(` | 24 | plus `always_redraw` 5, `f_always.` 6, `.always.` 12 |
| `FlashAround(` | 17 | emphasis ring |
| `ContextAnimation(` | 17 | word absorbs context |
| `RandomizeMatrixEntries(` | 15 | weights change |
| `CountInFrom(` | 14 | numbers count up from 0 |
| `make_number_changeable(` | 13 | templated subscripts and values |
| `ShowIncreasingSubsets(` | 10 | text appears word by word |
| `data_modifying_matrix(` | 10 | "learned from data" |
| `show_matrix_vector_product(` | 10 | row-by-row dot products |
| `VShowPassingFlash(` | 6 | plus 1 `ShowPassingFlash` |
| `turn_animation_into_updater(` | 6 | run an animation concurrently with waits |
| `FadeOutToPoint(` | 6 | "absorbed into here" |
| `UpdateFromAlphaFunc(` | 5 | custom interpolation |
| `DrawBorderThenFill(` | 5 | rectangles around tokens |
| `ChangeDecimalToValue(` | 4 | |

Parameter distributions: `lag_ratio` values are dominated by 0.1 (125 lines),
0.25 (55), 0.5 (54), 0.01 (52), 0.05 (33); `run_time` by 2 (142), 3 (74),
1 (50), 4 (34), 5 (25), with 8 to 30 second values reserved for camera orbits
and long processes.

### 5.2 Composite idioms worth naming

1. Plan-then-move. Build the final layout on `mob.target =
   mob.generate_target()`, mutate the target, then `MoveToTarget(mob)` in a
   single `play` alongside other animations (`network_flow.py:230-253`,
   `attention.py:179-221`). This separates layout logic from animation.
2. Reveal from source. `TransformFromCopy(source, result)` leaves the source
   in place, so "the matrix produces this vector" reads causally
   (`attention.py:413-415`, `mlp.py:589`). `FadeTransform(a.copy(), b)` is the
   text-to-text version (`network_flow.py:1171`).
3. Stagger inside one play. `time_span=(t0, t1)` on individual animations
   builds a mini-timeline within one `self.play(..., run_time=T)`
   (`chm.py:95-103`, `network_flow.py:568-575`, `embedding.py:383-387`).
4. Dim everything else. `set_opacity(0.25)` or `fade(0.75)` on the rest of a
   group, or `BackgroundRectangle` with 0.75 black fill laid over the parts to
   ignore (`attention.py:596-615`, `network_flow.py:754-769`).
5. Row-by-row dot product. `show_matrix_vector_product`
   (`helpers.py:97-159`): yellow rectangles sweep a row and the vector with
   `ShowIncreasingSubsets` while the output entry counts partial sums with
   `UpdateFromAlphaFunc` at `rate_func=linear`.
6. Numbers count in. `CountInFrom(Integer(...), 0)` paired with
   `GrowFromCenter(brace)` for dimensions and parameter counts
   (`embedding.py:553-557`, `network_flow.py:1148-1153`,
   `attention.py:2952-2957`).
7. Learned from data. `RandomizeMatrixEntries` plus flying "Data" words
   (`helpers.py:258-292`), or `MachineWithDials.random_change_animation`.
8. Sweep a flash along a copy. Copy lines, `insert_n_curves(20..100)`, thicken,
   then `LaggedStartMap(VShowPassingFlash, ...)` (`supplements.py:1975-1986`,
   `mlp.py:683-690`, `attention.py:3478-3485`).
9. Cycle a highlight. Loop over indices, each iteration dims all but one row
   or column and moves a rectangle (`embedding.py:435-447`, `mlp.py:834-854`,
   `attention.py:934-948`).
10. Live quantities. `f_always.set_value(lambda: ...)` and
    `always.next_to(...)` keep a decimal glued to geometry during rotations
    (`embedding.py:1791`, `mlp.py:1828-1837`, `ml_basics.py:1874-1876`).
11. Skip-render for long loops. `self.skip_animations = True` inside a loop,
    briefly un-skipped to flash a result (`generation.py:346-352`,
    `365-366`).
12. Succession fly-in. `Succession(FadeIn(x), x.animate.set_opacity(0).move_to(machine))`
    inside a `LaggedStart` for "lots of text into the machine"
    (`chm.py:212-222`, `mlp.py:88-96`, `auto_regression.py:509-519`).

## 6. Pacing and narrative structure

### 6.1 Beats

Every scene body is a sequence of blocks headed by a capitalized comment
("# Add sentence", "# Show embeddings", "# Collapse vectors"). There are 736
such comment lines across the ten scene files (88 in `supplements.py`, 149 in
`attention.py`, 119 in `embedding.py`, 97 in `mlp.py`). The comments read as
the outline of the narration, and each block ends with a `self.wait()`. The
ratio of `play` to `wait` lines is 1083 to 705; the default `wait()` (one
second) accounts for 542 of the waits, and longer holds of 2 to 5 seconds
follow key reveals (`self.wait(5)` appears 23 times, mostly at the end of
pi-creature shots so the editor can trim).

### 6.2 Tempo

- Default `run_time` is 2 seconds (142 lines), with 1 second for small
  confirmations and 3 to 4 for multi-part reveals.
- Long holds are for contemplation of 3D space: `wait(15)` after an orbit
  (`embedding.py:775`, `837`, `903`), `wait(20)` on the query-space map
  (`attention.py:1834`) and the final MJ space shot (`embedding.py:3014`,
  `3047`), `wait(30)` for ambient dots (`supplements.py:1590`).
- Rapid-fire loops use 0.1 to 0.25 second waits per example
  (`ml_basics.py:308`, `generation.py:489`, `chm.py:592`).

### 6.3 Narrative patterns observed

1. Concrete sentence first, abstraction second. Chapter 6 opens on "a fluffy
   blue creature roamed the verdant forest" (`attention.py:13`), shows arcs
   from adjectives to nouns, then introduces embeddings, then symbols, then
   queries and keys. Chapter 7 opens on "Michael Jordan plays Basketball"
   (`mlp.py:343`, `543`).
2. Preview, then detail. `MLPStepsPreview` shows Linear, ReLU, Linear as three
   arrows before `BasicMLPWalkThrough` spends 1300 lines on them
   (`mlp.py:277-293`). `HighLevelNetworkFlow` previews the whole network
   before any chapter explains a block.
3. The honest lie. `LyingAboutTokens2` puts "The Truth" (tokens) and "A
   Convenient Lie" (words) on screen together (`embedding.py:194-207`).
   `ThisIsMadeUp` and `NotQuiteTrue` are dedicated cutaways
   (`supplements.py:978-1000`).
4. Do one, then all in parallel. One vector passes through the MLP, then faded
   copies of the whole pipeline appear for every position
   (`mlp.py:504-540`, `1636-1651`); one column softmaxes, then every column
   (`attention.py:932-948`).
5. Count the parameters. Every chapter ends a block by bracing dimensions,
   counting in the integers and multiplying: embedding 50,257 by 12,288
   (`embedding.py:543-608`), unembedding (`network_flow.py:1115-1173`),
   query/key/value (`attention.py:2561-3011`), MLP 4 by 12,288 by 12,288 and
   the bias fraction 0.00008 (`mlp.py:949-1045`).
6. Ask the viewer's question. "What about these?" with arrows at the unused
   vectors (`network_flow.py:1037-1068`), student bubbles "What about
   cross-attention?" and "Is this how ChatGPT stores facts?"
   (`supplements.py:1101`, `1924`).
7. Admit what is skipped. `DetailsNotDiscussed` lists tokenization,
   positional encoding, layer normalization and training
   (`supplements.py:2133-2138`), and `OneThirdOfWhatYouNeed` strikes out "All"
   in the paper title (`supplements.py:1286-1312`).
8. Recurring cast of examples. The same phrases cross files: "Michael
   Jordan plays the sport of" (`auto_regression.py:456`, `supplements.py:1607`,
   `embedding.py:2767`), "Harry Potter ... Professor Snape"
   (`network_flow.py:724`, `ml_basics.py:1817`), the three "mole" sentences
   (`network_flow.py:1377-1381`, `embedding.py:2248-2252`), king and queen
   (`embedding.py:1124`), "the Computer History Museum is located in Mountain"
   (`network_flow.py:28`).

## 7. Text and Tex

- `Text` dominates: 353 lines versus `Tex` 174 and `TexText` 34. The font is
  CMU Serif via `custom_config.yml:27`; "GPT-3" is set in Consolas
  (`supplements.py:576`, `ml_basics.py:1177`).
- Substring selection on text mobjects drives most text animation:
  `phrase["mole"][0]` (`embedding.py:2256`), `title["Attention"][0]`
  (`supplements.py:880`), `equation["Q"]` (`attention.py:1882`), and regular
  expressions `weighted_sum[re.compile(r"w_\d|w_n")]` (`ml_basics.py:619`).
  `TransformMatchingStrings` morphs one string into another by shared
  substrings (`mlp.py:73`, `785`, `ml_basics.py:2286`).
- Templated numbers: `Tex(...).make_number_changeable("0")` returns a
  `DecimalNumber` inside the Tex that can be `set_value`d and copied
  (`attention.py:168-175`, `2285-2300`; defined at
  `manimlib/mobject/svg/tex_mobject.py:234`).
- Font-size ladder (lines): 72 (54) for titles and hero labels, 36 (29) for
  annotations, 60 (24), 24 (15), 90 (14), 30 (13), 48 (12, the default), and
  96, 120, 200, 250 for single-word impact ("Attention" at 250,
  `attention.py:1435`; dots at 250, `network_flow.py:548`).
- Math notation is sparse and bold-vector styled: `\vec{\textbf{E}}_i`,
  `\vec{\textbf{Q}}`, `W_Q`, `W_\uparrow`, `\Delta \vec{\textbf{E}}`
  (`attention.py:166`, `435`, `1184-1191`, `mlp.py:1048`). The one real
  equation shown is the attention formula, placed over the paper image
  (`attention.py:1858-1860`) and then decomposed term by term
  (`1905-2043`).
- Overlays on text use `set_backstroke(BLACK, 3..8)` and
  `set_fill(border_width=...)` for crispness at 4K (`network_flow.py:152`,
  `mlp.py:106`, `attention.py:3597`).
- Long prose is wrapped by `get_paragraph(words, line_len, font_size)`
  (`helpers.py:18-34`) and rendered left-aligned; a whole book page is a
  `TexText` with `\tiny` (`network_flow.py:1275`).
- Labels for numbers: `Integer(12288)`, `Integer(50257)`,
  `DecimalNumber(..., unit="%")` (`embedding.py:543`, `550`,
  `network_flow.py:622-627`).

## 8. Moves that make it good

Each move is a technique the framework should encode, with the evidence that
he uses it deliberately.

1. Show the real number, then the symbol, then the real number again. Vectors
   start as columns of decimals (`attention.py:81-84`), collapse to
   `\vec{E}_i` (`200-221`), and are re-expanded whenever a computation needs
   to be seen (`389-423`). The symbol is never introduced before the numbers.
2. Role colors are introduced once and never violated. Query yellow, key teal,
   value red hold from the first `Query` label (`attention.py:370`) through
   `MultiHeadedAttention` (`3590`) and the CHM talk.
3. Every abstraction gets a parameter count. See pattern 5 in section 6.3; the
   count is animated with braces and `CountInFrom`, and the product is
   `TransformFromCopy`-ed from its factors (`embedding.py:599-608`).
4. Dim, do not delete. When focus moves, the rest fades to 0.25 to 0.5 opacity
   rather than disappearing, so the viewer keeps the map
   (`attention.py:883-889`, `mlp.py:580-582`, `network_flow.py:301`).
5. The camera is a second narrator. Reorients coincide with topic shifts:
   look along the network when discussing depth (`network_flow.py:292-296`),
   face-on when discussing one vector (`network_flow.py:313`), tilt a column
   out of the plane to show softmax as a separate operation
   (`attention.py:893-929`).
6. Real model output where it is cheap. GPT-2 runs locally and GPT-3.5 is
   called for the bar charts (`generation.py:23-63`); real GloVe vectors
   position the words (`embedding.py:677`); real tokenization splits the text
   (`embedding.py:46-50`). Where reality would muddle the point, values are
   hand-set and the code says so: "Tweak queen for demo purposes"
   (`embedding.py:1148`), "Hack" (`2056-2059`), hand-authored attention types
   (`attention.py:3402-3446`), hand-set probabilities (`network_flow.py:29-38`).
7. Random but seeded. `random_seed` is a class attribute on scenes whose look
   depends on randomness (`mlp.py:391`, `ml_basics.py:395`, `chm.py:550`;
   21 lines overall), which makes re-renders reproducible.
8. One helper per visual noun. `WeightMatrix`, `NumericEmbedding`, `Dial`,
   `ContextAnimation`, `get_piece_rectangles` guarantee that the same concept
   looks the same in every chapter (section 2).
9. Motion with a reason. `FadeIn(x, shift=0.5 * DOWN)` moves in the direction
   of data flow (`attention.py:97`), `FadeOut(x, LEFT)` exits toward where the
   object came from (`supplements.py:119-120`), and `path_arc` makes a copy
   visibly travel rather than teleport (`attention.py:429`, `mlp.py:498`).
10. Keep the pipeline on screen. In `BasicMLPWalkThrough` the three-step
    pipeline (`mlp.py:456-487`) stays at the bottom while each step is blown
    up above it, and the collapsed expression is docked under its arrow when
    done (`mlp.py:1080-1086`, `1549-1555`).
11. Admit uncertainty inside the video. Pi creatures voice the viewer's doubt
    ("Isn't that outdated?", `supplements.py:599`; "Almost certainly not
    quite...", `1934`), and `MLPStepsPreview` labels "Structure: Easy" against
    "Emergent behavior: Exceedingly challenging" (`mlp.py:240-243`).
12. Scale is shown, not stated. 50 by 50 attention grid zooming out for 20
    seconds (`attention.py:2304-2309`), 9 by 9 grid of training machines with
    an exponentially growing frame (`chm.py:1278-1293`), nested timelines from
    a second to 100 million years (`chm.py:1592-1685`).
13. Transitions reuse geometry. Thumbnails become video icons
    (`supplements.py:494-497`), a highlight rectangle becomes the next
    rectangle (`supplements.py:759-760`), the "less" box becomes the "one" box
    (`attention.py:1634-1637`).
14. Micro-timing inside a single play. `time_span` lets a title appear at
    second 1 while a brace grows from second 0 and text writes at second 2
    (`network_flow.py:568-575`), which reads as a hand-edited cut rather than
    a chain of separate animations.

## 9. Counts table

### 9.1 Per file

| File | Lines | Classes | `play(` | `wait(` | `reorient(` | `fix_in_frame(` | Beat comments | Pi-creature scenes | 3D terms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `helpers.py` | 819 | 10 | 0 | 0 | 0 | 4 | 8 | 0 | 0 |
| `supplements.py` | 2252 | 79 | 189 | 147 | 0 | 1 | 88 | 35 | 0 |
| `embedding.py` | 3047 | 30 | 144 | 88 | 46 | 30 | 119 | 0 | 22 |
| `attention.py` | 4093 | 20 | 216 | 148 | 21 | 7 | 149 | 0 | 14 |
| `mlp.py` | 2627 | 16 | 184 | 118 | 30 | 1 | 97 | 0 | 13 |
| `network_flow.py` | 1531 | 14 | 74 | 32 | 23 | 7 | 56 | 0 | 10 |
| `generation.py` | 986 | 24 | 19 | 11 | 1 | 0 | 28 | 0 | 10 |
| `ml_basics.py` | 2430 | 14 | 140 | 93 | 0 | 0 | 90 | 0 | 5 |
| `chm.py` | 2160 | 38 | 98 | 61 | 15 | 0 | 84 | 3 | 12 |
| `auto_regression.py` | 599 | 10 | 19 | 7 | 3 | 0 | 17 | 0 | 7 |
| Total (unique) | 20544 | 255 | 1083 | 705 | 139 | 50 | 736 | 38 | 93 |

"3D terms" counts lines matching `ThreeDAxes`, `set_floor_plane`, `Cube(`,
`VCube`, `VPrism`, `DotCloud`, `OUT` or `IN`. "Pi-creature scenes" counts
lines containing `TeacherStudentsScene`. The 2026 file
`transformer_render.py` has 423 lines, 2 classes, 2 `play(`, 1 `wait(` and 6
`DotCloud` lines.

### 9.2 Primitive usage (lines, ten unique files)

| Primitive | Count | Primitive | Count |
| --- | ---: | --- | ---: |
| `Text(` | 353 | `Tex(` | 174 |
| `TexText(` | 34 | `Integer(` | 32 |
| `DecimalNumber(` | 18 | `NumericEmbedding(` | 31 |
| `WeightMatrix(` | 31 | `EmbeddingArray(` | 3 |
| `ImageMobject(` | 35 | `SVGMobject(` | 18 |
| `ThreeDAxes(` | 10 | `NumberPlane(` | 12 |
| `Axes(` | 17 | `DotCloud(` | 3 |
| `GlowDot` | 4 | `Cube(` | 4 |
| `VPrism(` | 2 | `Dodecahedron(` | 2 |
| `MachineWithDials(` | 10 | `Dial(` | 10 |
| `NeuralNetwork(` | 3 | `break_into_tokens(` | 7 |
| `break_into_words(` | 14 | `get_piece_rectangles(` | 20 |
| `softmax(` | 15 | `Mortimer(` | 10 |
| `change_students(` | 66 | `.says(` | 31 |
| `Blink(` | 17 | `np.random` | 49 |
| `random.` | 112 | `random_seed` | 21 |

## 10. Evolution 2017 to 2024

This section reports what the 2024 code itself shows. Statements about the
2017 series are limited to what is visible from this side (imports, deprecated
modules) and should be cross-checked against the sibling 2017 map.

1. Library. The scenes import `manim_imports_ext` (`manim_imports_ext.py:1-14`),
   which re-exports ManimGL (`from manimlib import *`) plus the legacy
   `old_tex_mobject` module and a `custom/deprecated.py`. `OldThoughtBubble`
   is still used as a shape source (`embedding.py:921`). So the 2024 code sits
   on ManimGL with a thin compatibility layer for older idioms.
2. Interactive workflow. Every scene is an `InteractiveScene`; the camera
   literals in `reorient` calls (section 4.2), the `self.embed()` call left in
   a comment block (`network_flow.py:273`), the "Start re-rendering here"
   note (`attention.py:1140`) and the `if self.window is not None:
   self.embed()` in the 2026 file (`transformer_render.py:422-423`) all point
   to scenes being authored live and camera positions being read off the
   window rather than computed.
3. 3D as the default stage. 93 lines of 3D vocabulary and 139 `reorient`
   lines; the signature shot of the series is the network receding along
   `OUT` (`network_flow.py:7-665`). Even 2D content is often placed in a
   `set_floor_plane("xz")` scene so the camera can tilt a column out of the
   plane (`attention.py:893`).
4. Data-driven scenes. Real tokenizer (`tiktoken`), real embeddings
   (`gensim` GloVe), a real local model (GPT-2 via `transformers` and
   `torch`), a hosted model (OpenAI completions with logprobs), and PyTorch
   optimization running inside an updater to spread vectors apart
   (`mlp.py:2483-2509`). Real architecture constants are typed into the
   scenes: 12,288; 50,257; 2,048; 128; 96; 175,181,291,520; 27,938
   (`embedding.py:543-550`, `network_flow.py:789-795`, `attention.py:2566-2567`,
   `3631`, `ml_basics.py:1188`, `1236`).
5. Abstraction level. The series runs a deliberate ladder: numbers, then
   symbols, then block diagrams, then a single cube per block. Helpers exist
   for each rung (`NumericEmbedding`, the `\vec{E}_i` template, `get_block`).
6. Scene length and file organization. Core scenes are 600 to 1400 lines and
   follow the script linearly; cutaways are split into `supplements.py` so the
   main files stay about one idea each. Variants are subclasses with
   attribute overrides rather than copies, except where the author notes
   "Largely copied ... could factor better later" (`embedding.py:2472`).
7. Generated imagery. DALL-E 3 illustrations are first-class mobjects
   (`attention.py:117-120`, `generation.py:760-811`), used to show meaning
   accumulating in a vector by baking copies of the image into the entries
   (`attention.py:1343-1360`).
8. 2026 direction. `transformer_render.py` imports `manimlib` directly
   (`:33`), subclasses plain `Scene` (`:404`), has no pi creatures, no text
   and no beats; it reconstructs a Houdini point-cloud layout as one
   `TransformerModel(Group)` of `DotCloud`s (`:104-370`) and animates a
   forward pass as a brightness wave over a `layer_depth` attribute with
   `UpdateFromAlphaFunc` (`:373-401`). Its docstring says values are
   synthesized deterministically and can be swapped for real GPT-2 tensors
   (`:24-27`). The trend is toward procedural, data-shaped geometry rendered
   as point clouds, with the camera doing the storytelling.

## 11. Data dependencies

None of the referenced data files or images are in the repository: a `find`
over the clone returns zero matches for every name below and zero image files
of any kind. `custom_config.yml:3-10` resolves `ImageMobject` and
`SVGMobject` names against directories under a Dropbox base path, and
`DATA_DIR` resolves to `<output dir>/2024/transformers/data/`
(`helpers.py:9`).

### 11.1 Models and services

| Dependency | Where | Scenes | Constraint for reproduction |
| --- | --- | --- | --- |
| `tiktoken` encoding for "davinci" | `embedding.py:9-10`, `46-50`, `525-531` | every `break_into_tokens` user: `LyingAboutTokens2`, `HighLevelNetworkFlow` family, `MJSpace`, `CostFunction`, `IntroduceEmbeddingMatrix` | pip install plus a one-time encoding download (network; **unverified** offline behavior) |
| GloVe `glove-wiki-gigaword-50` via `gensim.downloader` | `embedding.py:93-99`, `1900` | all `Word2VecScene` subclasses, `DotProductWith*Direction` | download on first run, cached to `DATA_DIR`; license of the GloVe data **unverified** |
| GPT-2 via `transformers` and `torch` | `generation.py:5-20`, `23-43` | default `model="gpt2"` in `SimpleAutogregression`, `PredictionVsGeneration` | Hugging Face download; CPU inference per sample |
| OpenAI completions `gpt-3.5-turbo-instruct` with `logprobs` | `generation.py:46-63`, `chm.py:607-619`, `ml_basics.py:2403` | all `model="gpt3"` scenes, `ChatbotFeedback`, `CostFunction` | needs `OPENAI_KEY`; uses the legacy `openai.Completion` interface (**unverified** against current SDK); output non-deterministic, code falls back to GPT-2 on exception (`generation.py:387-396`) |
| DALL-E 3 image generation | `generation.py:792-811` | `TextToImage.generate_output` (one-off) | produced static images, not needed at render time |
| ImageNet-1k via `datasets.load_from_disk` | `helpers.py:72-94` | `PremiseOfML`, `PremiseOfMLWithMatrices`, `FlashThroughImageData` | expects `~/Documents/image_net_1k`; the `datasets` import is commented out (`helpers.py:7`) |
| PyTorch optimizer inside a scene | `mlp.py:2483-2509`, `almost_orthogonal.py` | `SuperpositionVectorBundle` | torch at render time |
| SciPy `norm.cdf` | `mlp.py:2`, `1214`, `2560-2561` | GELU graph, layer-norm icon | scipy at render time |

### 11.2 Text corpora in `DATA_DIR`

| File | Where | Scenes |
| --- | --- | --- |
| `tale_of_two_cities.txt` | `helpers.py:68`, `ml_basics.py:339`, `979`, `chm.py:239`, `1260` (absolute path) | `FlashThroughTextData2`, `PremiseOfMLWithText`, `EvenMoreTextIntoMachine`, `ThousandsOfWords` |
| `harry_potter_3.txt` | `network_flow.py:1273` | `TextPassageIntro` |
| `murder_story.txt` | `attention.py:1456` | `MyseteryNovel` |
| `facts.txt` | `supplements.py:2227`, `auto_regression.py:502` | `ListOfFacts`, `AthleteCompletion` |
| `athlete_sports.txt` | `mlp.py:80` | `LastTwoChapters` |
| `pile_of_text.txt` | `chm.py:227` | `LotsOfTextIntoTheMachine` |
| `image_categories.txt` | `helpers.py:75` | ImageNet labels |
| `OWL3_Dictionary.txt` | `helpers.py:10` | defined, never used |

Copyrighted passages (Dickens is public domain; the Harry Potter excerpt and
the Frost poem typed at `attention.py:1551-1580` are not) constrain reuse.

### 11.3 Raster images and SVGs

Raster (resolved by name): `Dalle3_fluffy`, `Dalle3_blue`,
`Dalle3_creature`, `Dalle3_verdant`, `Dalle3_forest`, `Dalle3_creature_2`,
`BlueFluff`, `VerdantForest` (`attention.py:117-120`, `244-245`,
`2365-2367`); `SmallFluffCreature` (`embedding.py:270`); `ShrewMole`,
`LipMole` (`embedding.py:2273-2275`, `network_flow.py:1397-1399`);
`Tower1-4`, `EiffelTower1-3`, `MiniEiffelTower1` (`embedding.py:2378-2386`);
`AttentionPaper`, `AttentionPaperStill`, `NetworkEnd` (`supplements.py:734`,
`844`, `attention.py:1853`); `Zoolander`, `nn1-4_thumbnail.png`
(`supplements.py:135`, `458`); `AudioSnippet`, `PiCreatureDalle3_5`
(`generation.py:732`, `769`); `JohnRFirth`, `RiverBank`, `FederalReserve`,
`HumanAIScript`, `CHMTopText` (`chm.py:307`, `427-428`, `699`, `1858`).

Raster by absolute Dropbox path: chapter thumbnails (`supplements.py:465-467`,
`mlp.py:119-122`, `chm.py:13`), `EmbeddingStill.jpg` (`supplements.py:1469`),
`AttentionPattern0-4` (`attention.py:3544-3564`), `CHM_Exterior.jpeg`
(`chm.py:1881`). Remote: YouTube `maxresdefault.jpg` thumbnails by video id
(`chm.py:2124-2134`).

SVG: `ChatBot`, `OpenAI.svg`, `warning`, `and_gate` (`supplements.py:309`,
`577`, `1380`, `1729`); `gpu_large.svg` (`attention.py:4074`); `JaggedCurl1`,
`JaggedCurl2`, `TearOff`, `Bot`, `comp_worker`, `GenericComputer.svg`,
`History.svg`, `Museum.svg` (`chm.py:702`, `888`, `1394`, `1438`,
`1900-1902`). Pi-creature SVGs come from the `pi_creature_images` directory
(`custom_config.yml:9`).

### 11.4 Hand-entered model outputs

These are the numbers that make scenes look like real model behavior without
a model call: next-token probabilities (`network_flow.py:29-38`, `1180-1189`,
`882`), logprobs (`chm.py:897-898`, `1112`), an attention pattern for
cross-attention (`attention.py:3133-3141`), attention types and weights
(`attention.py:3402-3446`), softmax example logits (`ml_basics.py:1819`),
nearest neighbors of "jump" (`embedding.py:1720-1721`), and per-block
parameter counts "604M", "1.2B", "49K" (`mlp.py:2531-2533`).

### 11.5 What this means for reproduction

1. The scenes are not runnable from the repository alone; every chapter needs
   either the Dropbox assets or substitutes.
2. The three model dependencies that matter for teaching (tokenizer, GloVe,
   GPT-2) are open and downloadable; the OpenAI dependency is optional and the
   code already falls back to GPT-2.
3. The 2026 file demonstrates the alternative the skill should default to:
   deterministic synthetic values with a documented hook to swap in real
   tensors (`transformer_render.py:80-87`, `24-27`).
4. Illustrative images are a stylistic constant (DALL-E creatures, moles,
   towers); a reproduction either generates its own or substitutes
   emoji-free vector drawings.

## 12. Translation flags for ManimCE

The brief fixes ManimCE as the target. This section only records which ManimGL
idioms from the 2024 code have a same-named or obviously analogous class in
the ManimCE tree, based on `grep` over the ManimCE clone. Semantics and
signatures were not checked (the ManimCE docs site is blocked from this
container), so each row is a lead for the framework step, not a verified
mapping.

| ManimGL idiom (count) | Present in ManimCE source | Notes |
| --- | --- | --- |
| `InteractiveScene`, `self.embed()` | no | author with `Scene`; no live window in CE's Cairo renderer |
| `frame.reorient(theta, phi, gamma, center, height)` (139) | no `reorient` | `ThreeDScene.set_camera_orientation` / `move_camera` exist (`manim/scene/three_d_scene.py`) |
| `frame.add_ambient_rotation` (12) | `begin_ambient_camera_rotation` exists | same file |
| `fix_in_frame()` (50) | `add_fixed_in_frame_mobjects` on `ThreeDScene`; `fix_in_frame` only in `opengl_mobject.py` | HUD pinning is scene-level in CE |
| `set_floor_plane("xz")` (18) | no | CE's default camera already treats z as up; orientation math differs |
| `ShowCreation` (127) | no; `Create` exists | rename |
| `VShowPassingFlash` (6) | `ShowPassingFlash` exists | |
| `FlashAround` (17) | `Circumscribe`, `Indicate`, `Flash` exist | closest analog `Circumscribe`, **unverified** |
| `LaggedStart`, `LaggedStartMap` (393) | yes | |
| `TransformMatchingStrings` | `TransformMatchingShapes`, `TransformMatchingTex` exist | string-key semantics differ, **unverified** |
| `TransformFromCopy`, `FadeTransform`, `ReplacementTransform`, `MoveToTarget`, `Restore` | yes | |
| `generate_target`, `save_state`, `arrange_in_grid`, `get_grid` | yes (in `opengl_mobject.py`; Cairo `Mobject` **unverified** for `get_grid`) | |
| `ShowIncreasingSubsets`, `ShowSubmobjectsOneByOne` | yes | |
| `UpdateFromAlphaFunc`, `UpdateFromFunc`, `always_redraw`, `ValueTracker` | yes | `f_always` / `.always.` chaining **unverified** |
| `CountInFrom` (14) | not checked; `ChangeDecimalToValue` exists | |
| `DecimalMatrix`, `MobjectMatrix`, `IntegerMatrix` | yes | `ellipses_row` / `ellipses_col` arguments **unverified** |
| `BarChart`, `ThreeDAxes`, `NumberPlane`, `Brace`, `SurroundingRectangle`, `BackgroundRectangle` | yes | |
| `Cube`, `VPrism`, `DotCloud`, `GlowDot` | `Cube`, `Prism`, `Dot3D`, `PointCloudDot` exist | `DotCloud` glow and per-point rgba **unverified** |
| `Text["substring"]` indexing (hundreds of lines) | no equivalent found | CE `Text` supports `t2c` style maps; `MarkupText` exists; slicing by character index is the fallback |
| `make_number_changeable` (13) | not found | compose `MathTex` with a separate `DecimalNumber` |
| `set_backstroke` (40) | not found | `add_background_rectangle` exists; stroke outline needs `set_stroke(BLACK, ..., background=True)` **unverified** |
| `TexText` (34) | CE `Tex` is text-mode LaTeX, `MathTex` math-mode | rename, **unverified** semantics |
| Pi creatures, `ThoughtBubble`, `SpeechBubble` | no | custom assets; out of scope for the skill |
| Rate functions `there_and_back`, `there_and_back_with_pause`, `rush_from`, `wiggle`, `linear` | yes | |
| `random_bright_color(hue_range=...)` | `random_bright_color` exists | `hue_range` argument **unverified** |
| `custom_config` 3840 by 2160 at 30 fps, black background, CMU Serif | n/a | CE config keys differ; the look (black, serif, 4K) is reproducible |

## 13. Implications for the skill design

1. The visual vocabulary is small and helper-driven: token tape, numeric
   vector, weight matrix, collapsed symbol, machine with dials, slab stack,
   attention grid, embedding arrows, context arcs, bar chart. A pattern
   library that ships these ten objects as ManimCE classes with the same
   defaults (value ranges, ellipsis placement, color ramps) reproduces most of
   the look.
2. Role colors are a contract. The rubric should require a color legend per
   video and flag any symbol that changes hue.
3. Scenes should be written as beat lists. The 736 beat comments are the
   outline; a script-to-scene compiler can emit one block per narration
   sentence, each ending in a wait sized to the narration.
4. Default timings: 2 second plays, 1 second waits, `lag_ratio` 0.1 for
   crowds, 8 to 12 second camera orbits with nothing else moving.
5. Every abstraction needs a numbers pass and a parameter count; the rubric
   should check that each new object was first shown concretely.
6. Real data where it is free (tokenizer, GloVe, GPT-2), synthetic and seeded
   everywhere else, with the synthetic values hand-tuned to tell the truth
   the narration tells.
7. Camera moves must be planned, not read off a window. In CE, the skill
   needs a small camera helper that accepts the same (theta, phi, center,
   height) tuple and a convention for which beats get a move.
8. Pi-creature cutaways are not reproducible and should be replaced by text
   callouts or dropped; they carry pacing (the `wait(5)` holds) that the
   narration track can carry instead.

## Blocked or unverified

- The "Ultracode" tool named in the request does not exist in the kit (it was
  removed; `CHANGELOG.md:58`), so it was not used.
- ManimCE documentation at `docs.manim.community` is blocked from this
  container; all ManimCE statements rest on class and method names found in
  the cloned source, not on documented semantics.
- No video keyframes or transcripts were consulted; durations stated here are
  code `run_time` and `wait` values, not final edited timings.
- The GloVe data license, the current OpenAI SDK compatibility of
  `openai.Completion`, and offline behavior of `tiktoken` are unverified.
- `ml_basics.py` lines 1330 to 1814 and `chm.py` lines 700 to 880 and 1350 to
  1482 were not read; their class names appear in the inventory from `grep`.
- Upstream class names contain misspellings (`MyseteryNovel`,
  `SimpleAutogregression`, `DimensionComparrison`, `animate_prediction_ouptut`)
  that are quoted exactly; a spell-check gate may need an allowlist for them.

