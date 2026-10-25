# Map of the 2017 neural-network series source

This map describes what the ManimGL source for 3Blue1Brown's 2017 neural-network
series does and why it works as teaching, so that a ManimCE skill can borrow the
principles without copying the code (the source is CC BY-NC-SA 4.0; every
example in the eventual skill must be original). All claims cite `file:line` in
the read-only clone at `/home/user/3b1b/videos` unless marked otherwise. Counts
come from `grep` and from a small AST script; both are reproduced in section 9.

Scope and method:

- Files read end to end: `_2017/nn/part1.py` (4664 lines, chapters 1 and the
  ReLU footnote), `_2017/nn/part2.py` (3791 lines, chapter 2), `_2017/nn/part3.py`
  (4496 lines, chapters 3 and 4), `_2017/nn/network.py` (309 lines),
  `_2017/nn/playground.py` (178 lines), `_2017/gradient.py` (399 lines).
- Shared infrastructure consulted for citations: `custom/characters/pi_creature.py`,
  `custom/characters/pi_creature_scene.py`, `custom/filler.py`,
  `manim_imports_ext.py`, `custom_config.yml`, and a shallow clone of the
  ManimGL library at `/home/user/3b1b/manim` (from <https://github.com/3b1b/manim>)
  for default values. A shallow clone of ManimCE 0.22.0 at
  `/home/user/ManimCommunity/manim` (from <https://github.com/ManimCommunity/manim>)
  backs the translation notes, because `docs.manim.community` is blocked here.
- Identifiers are quoted verbatim, including the author's misspellings
  (`propogation`, `Minmization`, `Inactiviy`, `altnernate`), because they are the
  grep anchors. A repo that gates on `typos` needs `[default.extend-identifiers]`
  entries for them.

## 0. Files and how they fit together

| File | Lines | Classes | Scenes with `construct` | Role |
|---|---|---|---|---|
| `part1.py` | 4664 | 55 | 45 | Chapter 1 ("But what is a neural network?") plus the sigmoid-vs-ReLU footnote scenes at 4368-4544 |
| `part2.py` | 3791 | 61 | 49 | Chapter 2 (gradient descent); imports everything from `part1.py` (part2.py:7-8) |
| `part3.py` | 4496 | 35 | 26 | Chapters 3 and 4 (backpropagation, intuitive and calculus); imports `part1` and `part2` (part3.py:1-3) |
| `network.py` | 309 | 1 | 0 | Nielsen-style `Network` with `feedforward`, `SGD`, `backprop` (network.py:40-172), activation helpers, pretrained weights loader (198-206), MNIST image cache (269-289) |
| `playground.py` | 178 | 1 | 1 | Exploratory `Test` scene that draws weight rows and activation images; not part of the published videos |
| `gradient.py` | 399 | 10 | 6 | Stand-alone gradient and partial-derivative scenes. Not imported by any `nn/` file (grep), and it uses later APIs (`ValueTracker`, `always_shift`, `tex_to_color_map`, `FadeInFromDown`; gradient.py:52-56, 103-106). Treat as adjacent material, not series code |

Inheritance is the organizing device. `NetworkScene` (part1.py:274) builds a
network from `layer_sizes`; `PreviewMNistNetwork` (784) swaps in the pretrained
MNIST network; `IntroduceEachLayer` (1036) restyles it white; almost every
chapter-1 explanatory scene subclasses one of these. Chapter 2 adds
`PreviewLearning` (part2.py:142), which colors edges by weight sign and animates
real backprop steps, and chapters 2 to 4 subclass it (`IntroduceCostFunction`
585, `GradientNudging` 2576, `TestPerformance` 2772, `ShowAveragingCost`
part3.py:423, `SimplestNetworkExample` 2094). Multiple inheritance combines a
Pi-creature stage with a network stage by calling both `setup`s explicitly
(part1.py:619-623, 4141-4150; part2.py:1123-1126, 2973-2976).

Two render-workflow idioms matter for reproducing the pipeline:

- `self.force_skipping()` at the top of `construct` and
  `self.revert_to_original_skipping_status()` later (part1.py:626/768,
  2782-2785, 3018-3020; part2.py:2432/2556; part3.py:555/1239) make ManimGL skip
  rendering until the part being iterated on. The committed state of a scene
  therefore reflects the last partial render, not the whole scene. ManimCE's
  equivalents are `Scene.next_section(skip_animations=True)` and the
  `--from_animation_number` CLI option (verified by grep in the ManimCE clone;
  see the appendix).
- `ExternallyAnimatedScene` (custom/filler.py:4-6, raises on run) and
  `TODOStub` subclasses with a `message` naming an earlier scene (part3.py:35-53,
  part2.py:2571-2574, 2722-2725, 2968-2971) are placeholders for footage
  rendered elsewhere or re-inserted from an earlier scene. The video is
  assembled in an editor from many short scene renders; nothing in these files
  touches audio.

## 1. Scene inventory

Columns: `plays` and `waits` are counts of `self.play` and `self.wait` calls in
the class body (loops multiply them at run time); `wait s` sums explicit wait
durations with a bare `wait()` counted as 1 s (ManimGL default,
`manimlib/animation/animation.py:19` sets the default animation run time to 1.0
and `Scene.wait` defaults to 1 s); `rt s` sums explicit `run_time` values.
Teaching moves: hook, concrete, abstraction, formula, recap, aside, meta (plan,
transition, wrapper around inserted footage), outro, stub, thumbnail, utility.

### 1.1 part1.py (chapter 1 and the ReLU footnote)

| Class (line) | Base | What it visualizes | Move | plays / waits / wait s / rt s |
|---|---|---|---|---|
| `WrappedImage` (46) | `Group` | Image plus `SurroundingRectangle` | utility | 0 / 0 / 0 / 0 |
| `PixelsAsSquares` (60) | `VGroup` | One `Square` per pixel, fill opacity = alpha | utility | 0 / 0 / 0 / 0 |
| `PixelsFromVect` (80) | `PixelsAsSquares` | Same, from a 784-vector | utility | 0 / 0 / 0 / 0 |
| `MNistMobject` (87) | `WrappedImage` | Framed MNIST digit from a vector | utility | 0 / 0 / 0 / 0 |
| `NetworkMobject` (94) | `VGroup` | The network drawing (section 2) | utility | 0 / 0 / 0 / 0 |
| `MNistNetworkMobject` (262) | `NetworkMobject` | Pretrained 784-16-16-10 network | utility | 0 / 0 / 0 / 0 |
| `NetworkScene` (274) | `Scene` | Scene base with `feed_forward` | utility | 1 / 0 / 0 / 0 |
| `ExampleThrees` (336) | `PiCreatureScene` | Several handwritten 3s, 28px braces, "3 = 3" with pixels shown different | hook | 12 / 8 / 7.5 / 5 |
| `BrainAndHow` (527) | `Scene` | Brain SVG, "How?!?", passing flash on outline | hook | 2 / 1 / 1 / 2 |
| `WriteAProgram` (552) | `Scene` | Pixel grid with decimal values, arrow to digits 0-9, a hopping guess box | hook | 6 / 2 / 3 / 0 |
| `LayOutPlan` (619) | `TeacherStudentsScene`, `NetworkScene` | Words "Machine learning", "Neural network", network appears, formula preview, "Why the layers?", two video icons (Structure, Learning) | meta | 13 / 5 / 5 / 5 |
| `PreviewMNistNetwork` (784) | `NetworkScene` | 15 test digits fed forward, answer box | concrete | 4 / 0 / 0 / 1 |
| `AlternateNeuralNetworks` (847) | `PiCreatureScene` | CNN and LSTM named, "Maybe future videos?" | aside | 3 / 3 / 4 / 2 |
| `PlainVanillaWrapper` (891) | `Scene` | Title "Plain vanilla (aka multilayer perceptron)" | meta | 1 / 2 / 4 / 2 |
| `NotPerfectAddOn` (904) | `Scene` | Red "Not perfect!" with arrow | aside | 1 / 1 / 2 / 1 |
| `MoreAThanI` (920) | `TeacherStudentsScene` | Teacher: "More A than I" | aside | 0 / 1 / 2 / 0 |
| `BreakDownName` (929) | `Scene` | "Neural network" split into two questions; neuron = circle holding 0.2, 0.8, 0.4 ... | abstraction | 11 / 5 / 6 / 5 |
| `IntroduceEachLayer` (1036) | `PreviewMNistNetwork` | 784 pixels become neurons, one zoomed with live decimal, "Activation", fold into layer 0, output labels, "Hidden layers" with ?s, propagation | concrete to abstraction | 25 / 15 / 15 / 4 |
| `DiscussChoiceForHiddenLayers` (1337) | `TeacherStudentsScene` | "2 hidden layers", "16 neurons each", students ask why, teacher shrugs | aside | 6 / 5 / 5 / 6 |
| `MoreHonestMNistNetworkPreview` (1400) | `IntroduceEachLayer` | Preview with pixels flying into layer 0 | concrete | 1 / 0 / 0 / 2 |
| `AskAboutPropogationAndTraining` (1439) | `TeacherStudentsScene` | Two student questions | meta | 0 / 2 / 4 / 2 |
| `AskAboutLayers` (1454) | `PreviewMNistNetwork` | "Why the layers?" with arrows to every layer, boxes on hidden layers | hook | 3 / 2 / 2 / 3 |
| `BreakUpMacroPatterns` (1488) | `IntroduceEachLayer` | 9 = loop + line, 8 = loop + loop, 4 = three strokes; patterns placed beside layer 3 neurons; "Upper loop neuron...maybe..." | concrete to abstraction | 16 / 10 / 13 / 6 |
| `GenerallyLoopyPattern` (1740) | `Scene` | Flashes 8s and 9s every 0.2 s | concrete | 0 / 1 / 0.2 / 0 |
| `HowWouldYouRecognizeSubcomponent` (1754) | `TeacherStudentsScene` | Student: "recognizing loops is just as hard!" | hook | 1 / 1 / 1 / 0 |
| `BreakUpMicroPatterns` (1766) | `BreakUpMacroPatterns` | Loop = five colored edges; long line = three edges | abstraction | 8 / 5 / 7 / 8 |
| `SecondLayerIsLittleEdgeLayer` (1876) | `IntroduceEachLayer` | Hypothesized pipeline: pixels, edge-colored 9, pattern-colored 9, answer; "Does the network actually do this?" | abstraction | 11 / 5 / 6 / 10 |
| `EdgeDetection` (2090) | `Scene` | Lion photo morphs to Canny edges | concrete | 3 / 1 / 2 / 3 |
| `ManyTasksBreakDownLikeThis` (2108) | `TeacherStudentsScene` | Audio to letters to syllables to word | abstraction | 5 / 5 / 6 / 2 |
| `AskAboutWhatEdgesAreDoing` (2197) | `IntroduceEachLayer` | "What are these connections actually doing?" with arrows | hook | 0 / 1 / 1 / 0 |
| `IntroduceWeights` (2237) | `IntroduceEachLayer` | One neuron, its 784 incoming edges, parameter list becomes weights, weighted sum, weights as a pixel grid, positive region and negative border | formula | 20 / 12 / 16 / 28.5 |
| `MotivateSquishing` (2619) | `Scene` | Weighted sum maps to a number line; [0,1] interval; line squished by sigmoid | abstraction | 8 / 2 / 3 / 7 |
| `IntroduceSigmoid` (2717) | `GraphScene` | Sigmoid graph with formula; negative, positive, middle regions colored | formula | 3 / 3 / 3 / 0 |
| `IncludeBias` (2780) | `IntroduceWeights` | Sigma label, "How positive is this?", "> 10" becomes "-10", "bias" | formula | 10 / 7 / 11 / 10 |
| `BiasForInactiviyWords` (2958) | `Scene` | Banner "Bias for inactivity" | aside | 1 / 1 / 3 / 0 |
| `ContinualEdgeUpdate` (2968) | `VGroup` | Updater that cycles edge colors and widths | utility | 0 / 0 / 0 / 0 |
| `ShowRemainingNetwork` (3017) | `IntroduceWeights` | 784 weights per neuron, times 16, biases, remaining layers, "13,002"; "Learning = finding the right weights and biases" | formula to recap | 11 / 8 / 22 / 22.5 |
| `ImagineSettingByHand` (3236) | `Scene` | Randolph horrified at a thought bubble of a wandering network | aside | 4 / 3 / 12 / 0 |
| `WhenTheNetworkFails` (3261) | `MoreHonestMNistNetworkPreview` | Black box over hidden layers, a misclassified digit, "Wrong!" | hook | 4 / 2 / 11 / 3 |
| `EvenWhenItWorks` (3325) | `TeacherStudentsScene` | Teacher: "Even when it works, dig into why." | aside | 0 / 1 / 7 / 0 |
| `IntroduceWeightMatrix` (3334) | `NetworkScene` | 8-6 network; weighted sum of neuron 0; activations as a column; weights as a matrix; row meaning; bias vector; big sigma; clean `a1 = sigma(W a0 + b)` | formula | 38 / 9 / 12 / 15.5 |
| `HorrifiedMorty` (3889) | `Scene` | Mortimer horrified then hesitant | aside | 2 / 1 / 2 / 0 |
| `SigmoidAppliedToVector` (3903) | `Scene` | Sigma applied component-wise | formula | 0 / 1 / 1 / 0 |
| `EoLA3Wrapper` (3928) | `PiCreatureScene` | Screen rectangle, "Essence of linear algebra" | meta | 1 / 1 / 4 / 0 |
| `FeedForwardCode` (3944) | `ExternallyAnimatedScene` | Placeholder for code footage | stub | 0 / 0 / 0 / 0 |
| `NeuronIsFunction` (3947) | `MoreHonestMNistNetworkPreview` | "Neuron: thing that holds a number" crossed out, "Function"; one neuron as a function of the previous layer; whole network as `f(a_0..a_783)` | abstraction | 9 / 4 / 6 / 4 |
| `ComplicationIsReassuring` (4131) | `TeacherStudentsScene` | Student: "It kind of has to be complicated, right?" | aside | 1 / 1 / 4 / 0 |
| `NextVideo` (4141) | `MoreHonestMNistNetworkPreview`, `PiCreatureScene` | Training pairs flashed, video icon "On learning", Subscribe, output neurons become videos | outro | 10 / 7 / 21.2 / 3 |
| `NNPatreonThanks` (4302) | `PatreonThanks` | Credits | outro | 0 / 0 / 0 / 0 |
| `PiCreatureGesture` (4361) | `PiCreatureScene` | Gesture then happy | aside | 2 / 2 / 9 / 0 |
| `IntroduceReLU` (4368) | `IntroduceSigmoid` | Sigmoid crossed out as "Old school", slides away; ReLU graph; "Inactive" and "Same as f(a) = a" | formula | 11 / 5 / 9 / 1 |
| `CompareSigmoidReLUOnDeepNetworks` (4470) | `PiCreatureScene` | Two creatures hold up sigmoid ("Slow learner") and ReLU; a deep wandering network | aside | 4 / 2 / 11 / 1 |
| `ShowAmplify` (4546) | `PiCreatureScene` | Sponsor screen | outro | 3 / 2 / 12 / 0 |
| `Thumbnail` (4564) | `NetworkScene` | Thick-stroke network, "Neural Networks", "From the ground up" | thumbnail | 0 / 0 / 0 / 0 |
| `NeuralNetImageAgain` (4617) | `Scene` | Clean 16-16-16-10 network with brace | thumbnail | 0 / 0 / 0 / 0 |

### 1.2 part2.py (chapter 2)

| Class (line) | Base | What it visualizes | Move | plays / waits / wait s / rt s |
|---|---|---|---|---|
| `ShowLastVideo` (57) | `TeacherStudentsScene` | Screen with last video's title, "I assume you've watched this" | recap | 3 / 1 / 5 / 0 |
| `ShowPlan` (91) | `Scene` | Plan list; items dim to 0.5 except the current one | meta | 3 / 2 / 2 / 0 |
| `BeginAndEndRecap` (127) | `Scene` | `<Recap>` tag that turns into a closing tag | meta | 1 / 2 / 4 / 0 |
| `PreviewLearning` (142) | `NetworkScene` | "Training in progress..." with real backprop steps on 15 examples | concrete | 3 / 0 / 0 / 0.5 |
| `BackpropComingLaterWords` (323) | `Scene` | Caption "(Backpropagation be the next video)" | meta | 0 / 0 / 0 / 0 |
| `TrainingVsTestData` (330) | `Scene` | Two columns of labeled digits; "Train on these", "Test on these"; check marks; data scrolls | concrete | 4 / 3 / 3 / 0 |
| `MNistDescription` (425) | `Scene` | Title, authors, grids of (image, label) pairs cycling | concrete | 2 / 2 / 2 / 2 |
| `NotSciFi` (505) | `TeacherStudentsScene` | "Machines learning?!?", "It's actually just calculus.", "Even worse!" | hook | 0 / 3 / 4 / 3 |
| `FunctionMinmization` (541) | `GraphScene` | Dots roll downhill on a quartic by updater | abstraction | 0 / 1 / 10 / 0 |
| `ChangingDecimalWithColor` (576) | `ChangingDecimal` | Decimal whose fill tracks its value | utility | 0 / 0 / 0 / 0 |
| `IntroduceCostFunction` (585) | `PreviewLearning` | One neuron's formula, random init, feed a 3, "Utter trash", desired output, `(0.00 - 0.00)^2` terms, sum, average over data | formula | 25 / 10 / 12 / 19.5 |
| `YellAtNetwork` (1123) | `PiCreatureScene`, `PreviewLearning` | Randolph yells "Bad network!" at a network with eyes | hook | 8 / 2 / 2 / 2 |
| `ThisIsVeryComplicated` (1204) | `TeacherStudentsScene` | Teacher surprised, students guilty | aside | 0 / 1 / 2 / 1 |
| `EmphasizeComplexityOfCostFunction` (1214) | `IntroduceCostFunction` | Split screen: network as a function (784 in, 10 out, 13,002 parameters) then the cost function (parameters in, 1 number out) | abstraction | 8 / 6 / 5.75 / 2 |
| `NetworkGrowthMindset` (1412) | `YellAtNetwork` | "Awful!" then "Growth mindset!" | aside | 2 / 2 / 4 / 1 |
| `SingleVariableCostFunction` (1440) | `GraphScene` | `C(w)` graph, exact minimum, harder graph, step by slope, ball rolling, shrinking steps | abstraction | 29 / 15 / 20.5 / 8 |
| `LocalVsGlobal` (1810) | `TeacherStudentsScene` | "Local minimum = Doable, Global = Crazy hard" | aside | 0 / 1 / 2 / 0 |
| `TwoVariableInputSpace` (1819) | `Scene` | Input plane, eight candidate directions, gradient arrow, anti-gradient | abstraction | 7 / 4 / 6 / 3 |
| `CostSurface` (1926) | `ExternallyAnimatedScene` | Placeholder for 3D surface footage | stub | 0 / 0 / 0 / 0 |
| `KhanAcademyMVCWrapper` (1929) | `PiCreatureScene` | Screen for Khan Academy multivariable calculus | meta | 2 / 2 / 8 / 0 |
| `KAGradientPreview` (1943) | `ExternallyAnimatedScene` | Placeholder | stub | 0 / 0 / 0 / 0 |
| `GradientDescentAlgorithm` (1946) | `Scene` | Three lines: compute gradient, step, repeat | formula | 1 / 1 / 1 / 1 |
| `GradientDescentName` (1964) | `Scene` | Banner "Gradient descent" | meta | 1 / 1 / 1 / 2 |
| `ShowFullCostFunctionGradient` (1974) | `PreviewLearning` | Edges collapse into a 13,002-vector; negative gradient vector; components added in | formula | 7 / 2 / 2 / 3 |
| `DotsInsert` (2084) | `Scene` | Giant vertical dots | meta | 0 / 0 / 0 / 0 |
| `HowMinimizingCostMeansBetterTrainingPerformance` (2090) | `IntroduceCostFunction` | Output decimals move toward the target under "Minimize cost..." | concrete | 2 / 1 / 1 / 4 |
| `CostSurfaceSteps` (2139) | `ExternallyAnimatedScene` | Placeholder | stub | 0 / 0 / 0 / 0 |
| `ConfusedAboutHighDimension` (2142) | `TeacherStudentsScene` | "13,002-dimensional nudge?"; zoom into teacher's thought bubble | hook | 0 / 1 / 2 / 0 |
| `NonSpatialGradientIntuition` (2157) | `Scene` | Weight vector beside gradient vector; sign means increase or decrease; magnitude means a little, somewhat, a lot | abstraction | 5 / 4 / 6 / 0 |
| `SomeConnectionsMatterMoreThanOthers` (2318) | `PreviewLearning` | One edge "matters a lot", another "who even cares" | concrete | 3 / 2 / 2 / 0 |
| `SpinningVectorWithLabel` (2387) | `Scene` | Rotating vector with live cos and sin label | abstraction | 1 / 1 / 1 / 8 |
| `TwoGradientInterpretationsIn2D` (2431) | `Scene` | `C(x,y)`, gradient at (1,1), steepest ascent arrow, relative importance of x and y, wiggles in a neighborhood | formula | 12 / 6 / 7 / 11 |
| `ParaboloidGraph` (2568) | `ExternallyAnimatedScene` | Placeholder | stub | 0 / 0 / 0 / 0 |
| `TODOInsertEmphasizeComplexityOfCostFunctionCopy` (2571) | `TODOStub` | Re-insert marker | stub | 0 / 0 / 0 / 0 |
| `GradientNudging` (2576) | `PreviewLearning` | Gradient vector of decimals; edges change by a small multiple, gradient recomputed, ten times | concrete | 6 / 1 / 1 / 4 |
| `BackPropWrapper` (2702) | `PiCreatureScene` | Screen "Backpropagation (next video)" | meta | 4 / 2 / 6 / 2 |
| `TODOInsertCostSurfaceSteps` (2722) | `TODOStub` | Re-insert marker | stub | 0 / 0 / 0 / 0 |
| `ContinuouslyRangingNeuron` (2727) | `PreviewLearning` | One neuron enlarged with a decimal that ranges 0.23 to 0.97 | concrete | 2 / 1 / 1 / 0 |
| `AskHowItDoes` (2764) | `TeacherStudentsScene` | "How well does it do?" | hook | 0 / 1 / 5 / 0 |
| `TestPerformance` (2772) | `PreviewLearning` | 300 test digits at 0.1 s each; running fraction and decimal; "Wrong!" lingers 0.5 s | concrete | 0 / 2 / 2 / 0 |
| `ReactToPerformance` (2923) | `TeacherStudentsScene` | "98% testing accuracy", "State of the art is 99.79%" | aside | 1 / 2 / 2 / 3 |
| `NoticeWhereItMessesUp` (2955) | `TeacherStudentsScene` | "Look where it messes up" | meta | 0 / 1 / 2 / 1 |
| `WrongExamples` (2963) | `TestPerformance` | Same run with no delay between examples | concrete | 0 / 0 / 0 / 0 |
| `TODOBreakUpNineByPatterns` (2968) | `TODOStub` | Re-insert marker for the chapter-1 pattern scene | stub | 0 / 0 / 0 / 0 |
| `NotAtAll` (2973) | `TeacherStudentsScene`, `PreviewLearning` | "Well... not at all!" with the punchline hidden in black then revealed | aside | 1 / 1 / 2 / 1 |
| `InterpretFirstWeightMatrixRows` (2998) | `TestPerformance` | Each hidden neuron's weights drawn as a 28x28 blue and red image | concrete | 5 / 1 / 1 / 0 |
| `InputRandomData` (3090) | `TestPerformance` | Random noise fed in; "What might you expect?"; "What?!?"; network says "Looks like a 5 to me!" | concrete | 12 / 4 / 4 / 6 |
| `CannotDraw` (3228) | `PreviewLearning` | "Draw a 5 for me" versus "I'm really more of a multiple choice guy" | aside | 5 / 1 / 1 / 1 |
| `TODOShowCostFunctionDef` (3264) | `TODOStub` | Re-insert marker | stub | 0 / 0 / 0 / 0 |
| `TODOBreakUpNineByPatterns2` (3269) | `TODOBreakUpNineByPatterns` | Re-insert marker | stub | 0 / 0 / 0 / 0 |
| `SomethingToImproveUpon` (3272) | `PiCreatureScene`, `TestPerformance` | Series timeline, "Old technology!", CNN and LSTM, validation montage, hidden layers boxed | meta | 7 / 6 / 12 / 2 |
| `ShiftingFocus` (3405) | `Scene` | "How do neural networks learn?" becomes "Do video viewers learn?" | aside | 4 / 3 / 5 / 2 |
| `PauseAndPonder` (3432) | `TeacherStudentsScene` | "Pause and ponder!" | meta | 1 / 1 / 6 / 1 |
| `ConvolutionalNetworkPreview` (3448) | `Scene` | Two 4x4 kernels sweep a digit frame by frame | concrete | 0 / 1 / 1 / 0 |
| `RandomlyLabeledImageData` (3489) | `Scene` | Ten images whose labels are shuffled | concrete | 2 / 2 / 2 / 7 |
| `TrainOnImages` (3547) | `PreviewLearning`, `RandomlyLabeledImageData` | A six-layer network re-randomizes edges per image | concrete | 1 / 0 / 0 / 2 |
| `IntroduceDeepNetwork` (3594) | `Scene` | Empty | stub | 0 / 0 / 0 / 0 |
| `AskNetworkAboutMemorizing` (3598) | `YellAtNetwork` | "Are you just memorizing?"; network looks sad | hook | 2 / 2 / 2 / 2 |
| `CompareLearningCurves` (3616) | `GraphScene` | Cost versus steps for random and proper labels, drawn over 12 s each | concrete | 6 / 2 / 2 / 24 |
| `ManyMinimaWords` (3689) | `Scene` | "Many local minima, roughly equal quality" | aside | 1 / 1 / 1 / 0 |
| `NNPart2PatreonThanks` (3701) | `PatreonThanks` | Credits | outro | 0 / 0 / 0 / 0 |

### 1.3 part3.py (chapters 3 and 4)

| Class (line) | Base | What it visualizes | Move | plays / waits / wait s / rt s |
|---|---|---|---|---|
| `LayOutPlan` (5) | `Scene` | Bulleted plan: Recap, Intuitive walkthrough, Derivatives in computational graphs; screen rectangle | meta | 2 / 1 / 2 / 2 |
| Four `TODOInsert...` (35-53) | `TODOStub` | Re-insert feed-forward, cost-surface steps, cost definition, gradient nudging | stub | 0 / 0 / 0 / 0 |
| `InterpretGradientComponents` (55) | `GradientNudging` | Cost readout drops as weights nudge; "Direction in 13,002 dimensions?!?"; two weights isolated with number lines; nudging one moves the cost 32 times more than the other | formula | 19 / 4 / 5 / 9 |
| `GetLostInNotation` (350) | `PiCreatureScene` | Four backprop equations; Morty pleads; symbols dissolve into circles | hook | 3 / 3 / 4 / 2 |
| `TODOInsertPreviewLearning` (418) | `TODOStub` | Re-insert marker | stub | 0 / 0 / 0 / 0 |
| `ShowAveragingCost` (423) | `PreviewLearning` | Output versus desired with "Cost of one example"; examples stream at 15 per second; "Each step uses every example ...theoretically" | recap | 3 / 3 / 3 / 4 |
| `FocusOnOneExample` (540) | `TeacherStudentsScene` | "Focus on just one example" | meta | 0 / 1 / 2 / 0 |
| `WalkThroughTwoExample` (545) | `ShowAveragingCost` | The intuitive backprop walkthrough on a 2: desired nudges, one output neuron's formula, three ways to raise it, Hebbian aside, nudges requested of the previous layer, summing requests, recursion | concrete to abstraction | 71 / 34 / 34.5 / 35 |
| `WriteHebbian` (1390) | `Scene` | Banner "Hebbian theory" | aside | 1 / 1 / 1 / 0 |
| `NotANeuroScientist` (1398) | `TeacherStudentsScene` | Brain versus network with "???"; "No claims here..."; asterisks | aside | 6 / 2 / 2 / 3 |
| `ConstructGradientFromAllTrainingExamples` (1463) | `Scene` | Grid of per-example requested changes with eyes on each digit; rows averaged; collapse into negative gradient with eta | formula | 17 / 4 / 4 / 4 |
| `WatchPreviousScene` (1833) | `TeacherStudentsScene` | Screen, students thinking | meta | 1 / 1 / 10 / 0 |
| `OpenCloseSGD` (1848) | `Scene` | `<Stochastic gradient descent>` opening and closing tag | meta | 2 / 2 / 4 / 0 |
| `OrganizeDataIntoMiniBatches` (1868) | `Scene` | 60 digits shuffled, split into rows, each row highlighted as a step | concrete | 8 / 4 / 4 / 10 |
| `SGDSteps`, `GradientDescentSteps` (2012-2016) | `ExternallyAnimatedScene` | Placeholders for drunk-walk footage | stub | 0 / 0 / 0 / 0 |
| `SwimmingInTerms` (2018) | `TeacherStudentsScene` | Four terms; students horrified; "Backpropagation" kept | recap | 2 / 2 / 2 / 0 |
| `BackpropCode`, `BackpropCodeAddOn` (2041-2059) | stub, `PiCreatureScene` | Nielsen code footage with caption | meta | 2 / 1 / 2 / 0 |
| `CannotFollowCode` (2061) | `TeacherStudentsScene` | "I can't follow that code"; "Let's get to the calculus then" | hook | 2 / 2 / 4 / 1 |
| `EOCWrapper` (2083) | `Scene` | Screen "Essence of calculus" | meta | 1 / 1 / 1 / 0 |
| `SimplestNetworkExample` (2094) | `PreviewLearning` | Network collapses to 1-1-1-1; cost of six parameters; labels, desired output, cost, activation formula, z, computational graph, number lines with linked dots, sensitivity, chain rule, each derivative, average, gradient, derivatives with respect to b and previous a, long path | formula | 136 / 61 / 71.7 / 47.2 |
| `IsntThatOverSimplified` (3623) | `TeacherStudentsScene` | "Isn't that over-simplified?"; "Not that much, actually!" | hook | 0 / 2 / 3 / 2 |
| `GeneralFormulas` (3641) | `SimplestNetworkExample` | 3-3-2 network with subscripts j and k; sum cost; `w_jk` on its edge; chain rule with gradient-colored boxes; sum over paths; previous layer | formula | 39 / 19 / 20 / 12.5 |
| `ThatsPrettyMuchIt`, `PatYourselfOnTheBack`, `ThatsALotToThinkAbout` (4196-4221) | `TeacherStudentsScene` | One-line reactions | outro | 0 / 3 / 9 / 1 |
| `LayersOfComplexity` (4223) | `Scene` | The three chain-rule equations stacked, braced into the gradient | recap | 4 / 1 / 1 / 0 |
| `SponsorFrame` (4287) | `PiCreatureScene` | Sponsor screen | outro | 12 / 5 / 16 / 5 |
| `NN3PatreonThanks` (4344) | `PatreonThanks` | Credits | outro | 0 / 0 / 0 / 0 |
| `Thumbnail`, `SupplementThumbnail` (4415-4476) | `PreviewLearning` | Network with arrow tips pointing backward, "Backpropagation" | thumbnail | 0 / 0 / 0 / 0 |

### 1.4 Size distribution

Of 120 scenes with `construct`, five carry most of the explanatory weight:
`SimplestNetworkExample` (1528 lines, 136 plays), `WalkThroughTwoExample` (844,
71), `IntroduceWeightMatrix` (554, 38), `GeneralFormulas` (554, 39),
`IntroduceCostFunction` (537, 25). Thirty-six scenes are under 20 lines and are
Pi-creature one-liners, banners or stubs. The chapter is therefore a few long
"spine" scenes separated by many short reaction and transition scenes.

## 2. Visual abstractions

### 2.1 Image and pixel helpers (part1.py:46-92, 325-333)

- `WrappedImage(image_mobject, rect_kwargs)` wraps any image in a
  `SurroundingRectangle` (default `BLUE`, `SMALL_BUFF`; 47-51).
- `PixelsAsSquares(image_mobject, height=2)` makes one `Square` per pixel with
  `stroke_width=0` and `fill_opacity = alpha/255`, arranged with
  `arrange_in_grid(..., buff=0)` and `replace(image_mobject)` (60-78). This is
  what lets pixels be animated individually: `LaggedStartMap(DrawBorderThenFill,
  three)` (595), `sort(lambda p: np.dot(p, DOWN+RIGHT))` for diagonal reveal
  (344, 556), pixels flying into neurons (828-838).
- `PixelsFromVect(vect)` and `MNistMobject(vect)` build those from a flat
  784-vector through `layer_to_image_array` (network.py:228-234).
- `make_transparent(image_mob)` copies the red channel into alpha and whitens
  the image, so handwritten strokes can be recolored and overlaid (325-333,
  used at 1696, 1930).

### 2.2 `NetworkMobject` (part1.py:94-260)

Parameters exposed through `CONFIG` (95-111):

| Key | Default | Effect |
|---|---|---|
| `neuron_radius` | 0.15 | Circle radius; 0.3 to 0.35 for small networks (part1.py:3340, part3.py:2149, 3647) |
| `neuron_to_neuron_buff` | `MED_SMALL_BUFF` | Vertical gap; `SMALL_BUFF` for MNIST (263), `LARGE_BUFF` for the 3-3-2 network (part3.py:3646) |
| `layer_to_layer_buff` | `LARGE_BUFF` | Horizontal gap; 1.5 (266), 2 (1879), 2.5 (1340), 3 (part3.py:58) as the frame needs |
| `neuron_stroke_color`, `neuron_stroke_width` | `BLUE`, 3 | Restyled to `WHITE`, 2 in every explanatory scene from `IntroduceEachLayer` on (1039-1040) |
| `neuron_fill_color` | `GREEN` | Activation fill; `WHITE` from 1041 onward, so activation reads as brightness |
| `edge_color`, `edge_stroke_width` | `GREY_B`, 2 | Inert connections; width 1 for MNIST (265) |
| `edge_propogation_color`, `edge_propogation_time` | `YELLOW`, 1 | Color and duration of the signal flash; `GREEN` in chapter 2 (part2.py:153) |
| `max_shown_neurons` | 16 | Layers above this show 16 circles around `\vdots` (152-163) |
| `brace_for_large_layers` | True | Brace with the true size, e.g. 784 (164-169) |
| `average_shown_activation_of_large_layer` | True | Collapse 784 activations to 16 by block statistics (199-216) |
| `include_output_labels` | False | Digits 0-9 beside the last layer (250-259) |

Structure: `layers` is a `VGroup` of layer groups, each with `.neurons`, optional
`.dots`, `.brace`, `.brace_label` (130-171); every neuron gets `edges_in` and
`edges_out` groups (142-144, 178-181); `edge_groups` holds one group of
`Line`s per layer pair and is added to the back (173-183). Behaviour:
`get_active_layer(i, vector)` returns a deep copy with fills set (194-197),
which scenes `Transform` into (`show_activation_of_layer`, 301-314);
`activate_layers(input)` runs the real network and sets all fills (225-228);
`deactivate_layers` zeroes them (230-236); the propagation helper copies an edge
group, sets it to the propagation color at 1.5x width and plays
`ShowCreationThenDestruction(..., lag_ratio=0.5)` (238-248).

`MNistNetworkMobject` (262-272) loads `get_pretrained_network()` so every fed
digit shows the true activations of a trained 784-16-16-10 network
(`DEFAULT_LAYER_SIZES`, network.py:33).

### 2.3 `NetworkScene` and `PreviewLearning`

`NetworkScene` (part1.py:274-323): `layer_sizes` default `[8, 6, 6, 4]` (276),
`feed_forward(input, false_confidence, added_anims)` animates layer by layer
with the edge flash (285-314); `remove_random_edges(prop=0.9)` thins the
drawing (316-322), called with 0.7 in most MNIST scenes (790, 1332, 1680, 1896,
2208).

`PreviewLearning` (part2.py:142-321) adds the learning vocabulary:
`color_network_edges` sets each edge to `positive_edge_color` or
`negative_edge_color` with width `max_stroke_width * (|w| / max)^stroke_width_exp`
(285-301); `activate_network` plays a yellow `ShowCreationThenDestruction` over
all edges (`lag_ratio=0.3`) while layers transform with `lag_ratio=0.5` and
`rate_func=linear` (194-217); `backprop_one_example` calls the real
`network.backprop`, draws per-layer deltas in `positive_change_color` and
`negative_change_color`, applies an `eta=3.0` step and recolors (219-273);
`get_edge_animation` is the "wiggle the weights" idiom (303-312).

### 2.4 Numbers and vectors

- Decimal readouts inside neurons: `DecimalNumber` set to 0.7 to 0.85 of the
  neuron width, `BLACK` when the fill opacity exceeds 0.8 and `WHITE` otherwise
  (part1.py:1117-1123, 1272-1279; part2.py:2746-2751; part3.py:3565-3572).
  Updated live with `ChangingDecimal` plus `UpdateFromFunc` for the color flip.
- `get_decimal_vector(nums, with_dots)` (part2.py:24-53) builds a bracketed
  column of signed decimals colored `POSITIVE_COLOR`/`NEGATIVE_COLOR`
  (BLUE/RED, 10-11), with `\big[ \big]` brackets scaled 2x and stretched to
  1.2x the content height; the same bracket recipe appears at part1.py:3880-3886,
  part2.py:1992-1997, 2186-2190, part3.py:3301-3307.
- `ChangingDecimalWithColor` (part2.py:576-583) dims a decimal in proportion to
  its value.
- `set_variables_as_attrs(...)` (25 uses in part3.py) stores step outputs for
  later steps; chapter 1 does the same by hand (`self.neurons = neurons`, 1105).

### 2.5 `ContinualEdgeUpdate` (part1.py:2968-3015)

A `VGroup` with an updater that gives every edge a random cycle of colors
(`[GREEN, GREEN, GREEN, RED]`, 2973) and widths (`max_stroke_width *
random()**stroke_width_exp`, 2984-2987) and interpolates between them with a
per-edge `cycle_time` of 1 to 2 s. It is the visual for "weights wandering" or
"learning in progress" (3200, 3246, 3312, 4172, 4507, 4588; part2.py:1416,
3280; part3.py:1416). The file's own header warns that `ContinualAnimation` is
deprecated (part1.py:9-14); the class already uses `add_updater` (2995).

### 2.6 Shared stage infrastructure (outside `nn/`)

- `PiCreatureScene` (custom/characters/pi_creature_scene.py:37-61): one
  `BLUE` creature in the lower-left corner by default (`default_pi_creature_start_corner = DL`).
- `TeacherStudentsScene` (255-304): three students (`BLUE_D`, `BLUE_E`, `BLUE_C`,
  scaled 0.8) in the lower left, a `GREY_BROWN` teacher in the lower right, a
  `GREY_E` full-screen background, and a black `ScreenRectangle` of height 4 in
  the upper left for inserted footage. `teacher_says`, `student_says(index=2)`,
  `play_student_changes`, `change_students(lag_ratio=0.5, run_time=1)` are the
  verbs (306-363).
- `Eyes(body, height)` (custom/characters/pi_creature.py:368-420) puts a
  creature's eyes on any mobject; the series uses it to make the network itself
  a character (part2.py:1197, 3200, 3236; part3.py:1763).
- `ExternallyAnimatedScene` (custom/filler.py:4-6) raises if run.
- `TODOStub` and `PatreonThanks` are used (part2.py:2571, 3701) but their
  definitions were not located under `custom/` by grep; unverified.

### 2.7 How scenes compose these pieces

A typical chapter-1 spine scene: subclass `IntroduceEachLayer`, override
`setup_network_mob` to scale the network to 0.7 or 0.8 and `to_edge(DOWN)`
(part1.py:1893-1896, 3271-3273, 3960-3963), thin edges, then write `construct`
as a list of 5 to 13 step methods (1047-1053, 1497-1505, 2245-2253). Each step
places its objects relative to the network (`next_to(network_mob, LEFT,
MED_SMALL_BUFF, UP)`), plays 1 to 6 animations, and stores what the next step
needs. Chapter 3 pushes this to 31 steps in `SimplestNetworkExample`
(part3.py:2102-2135), with a `comp_graph` attribute bag for the computational
graph (2566-2574) and a helper `get_all_comp_graph_parts` (3574-3585).

## 3. Color system

Hex values are ManimGL defaults (`/home/user/3b1b/manim/manimlib/default_config.yml:144-198`;
aliases `BLUE = BLUE_C` etc. at `manimlib/constants.py:140-148`). ManimCE's
constants of the same name have the same hex values for these entries
(unverified here; check `manim/utils/color/manim_colors.py` in the CE clone).

| Name (hex) | Uses in the three files | Semantic roles with evidence |
|---|---|---|
| `YELLOW` (#FFFF00) | 103 | Emphasis and attention: signal flash along edges (part1.py:104, 1883), highlighted words ("Hidden layers" 1300, "Activation" 1159, "Mini-batches" 1921 in part3), sigma and its parentheses (part1.py:2947, 3539; part2.py:661; part3.py:843, 2986), weight vector symbol `W` (part2.py:2013, 2159), desired output `y` (part3.py:2099), tangent lines (part2.py:1448), question text (part2.py:1857), the thumbnail subtitle (part1.py:4587) |
| `WHITE` (#FFFFFF) | 101 | Neuron strokes and activation fill from `IntroduceEachLayer` on (part1.py:1039-1041), neutral arrows (part2.py:1827, 2630), decimal text, split lines |
| `BLUE` (#58C4DD) | 78 | Positive weights and positive changes in chapters 2 to 4 (part2.py:10, 161, 163; part3.py:841, 3315), "bias" in chapter 1 (part1.py:2898, 3478), labels and category words ("Neural network" 637, "Input:" part2.py:1382), MNIST frames (part1.py:48, 798), pointer arrows (part1.py:355, 584), "We'll get back to this" (2038), "Propagate backwards" (part3.py:1303) |
| `RED` (#FC6255) | 70 | Negative weights (part1.py:2240; part2.py:11, 162), cost everywhere (part2.py:837, 1089, 1319, 1454; part3.py:2098), "Wrong!" and "Not perfect!" (part1.py:905, 3300; part2.py:2846), anti-gradient (part2.py:1905), "Old school" (part1.py:4387), desired-activation decrease arrows (part3.py:716) |
| `GREEN` (#83C167) | 44 | Positive weights in chapter 1 (part1.py:2239, 2403, 3454, 3808), "Machine learning" (636), gradient direction of steepest ascent (part2.py:1884, 1898), correct count and check marks (part2.py:372, 2793, 2934), `z` in chapter 4 (part3.py:2097), "Same as f(a) = a" (part1.py:4456) |
| `BLACK` (#000000) | 27 | Text on bright neurons (threshold 0.8), masking rectangles that hide what is not yet relevant (part1.py:3277-3281; part3.py:1307-1311), hidden punchline (part2.py:2976) |
| `MAROON_B` (#EC92AB) | 16 | Bias in chapters 2 to 4 (part2.py:590; part3.py:842, 2985, 3317), learning rate eta (part3.py:1733), "16 neurons each" (part1.py:1350), the second isolated weight (part3.py:177) |
| `GREY_B` (#BBBBBB) | 12 | Inert edges (part1.py:102), de-emphasized edges (part3.py:206), grid lines and number lines (part3.py:1477, 1485, 2652), brains and frames (part1.py:530) |
| `TEAL` (#5CD0B3) | 3 | A contrasting "other" item: the unimportant weight (part2.py:2344), the `y` term (part2.py:2530), `z` in the notation scene (part3.py:383) |
| `BLUE_C`, `BLUE_D`, `BLUE_E`, `BLUE_B`, `RED_B`, `GREEN_B`, `PURPLE`, `PINK` | 1 to 2 each | Shades for change colors (part2.py:163), decimal signs (1986, 2039), rectangle tints (part1.py:3618), gradients |

Consistency assessment:

- Stable across all chapters: cost is `RED`; sigma is `YELLOW`; emphasis,
  flashes and newly named terms are `YELLOW`; activations are white brightness;
  inert structure is `GREY_B` or thin white; negative is `RED`.
- Drift between chapters: positive weights are `GREEN` in chapter 1
  (part1.py:2239) and `BLUE` from chapter 2 on (part2.py:10, 161); bias is
  `BLUE` in chapter 1 (part1.py:2898, 3478) and `MAROON_B` afterwards
  (part2.py:590). The later convention (weights `BLUE`, bias `MAROON_B`, `z`
  `GREEN`, cost `RED`, sigma and desired output `YELLOW`) is the one the
  final formula scenes use (part3.py:2095-2099, 3314-3318, 4273-4278) and is the
  better one to adopt.
- Coloring is applied semantically through `set_color_by_tex` and
  `set_color_by_tex_to_color_map` (23 calls), e.g. part1.py:3805-3810,
  part2.py:644-661, part3.py:376-384, so a term keeps its color whether it
  appears in a formula, a label or a column vector.
- Background: `custom_config.yml` sets `#000000` at 3840x2160, 30 fps
  (lines 20-24); `TeacherStudentsScene` paints `GREY_E` (#222222) behind the
  classroom (pi_creature_scene.py:258, 265-272). ManimCE's default background
  is `BLACK` (`manim/_config/default.cfg:49` in the CE clone).

## 4. Layout and composition

Frame geometry: ManimGL's frame is 8 units tall (`default_config.yml:119`) and
16:9, so `FRAME_WIDTH` is about 14.2 and `FRAME_X_RADIUS` about 7.1. Buffers:
`SMALL_BUFF` 0.1, `MED_SMALL_BUFF` 0.25, `MED_LARGE_BUFF` 0.5, `LARGE_BUFF` 1.0
(`default_config.yml:122-125`); `next_to` defaults to 0.25 and `to_edge` to
0.5 (127-128). ManimCE uses the same frame height and buffer values
(unverified here; the CE `constants.py` was not read).

Measured habits (all three files):

| Habit | Count | Evidence |
|---|---|---|
| `SMALL_BUFF` | 144 | Default spacing between a label and the thing it labels |
| `MED_LARGE_BUFF` | 51 | Between a rectangle and its caption (part1.py:1962, 3285) |
| `LARGE_BUFF` | 46 | Between a diagram and the next column of content (part1.py:1081, 2287) |
| `MED_SMALL_BUFF` | 37 | Inside compact groups |
| `to_edge(UP)` | 52 | Titles, questions and formulas live at the top (part1.py:688, 1464, 2217, 2451) |
| `to_edge(DOWN)` | 26 | The network lives at the bottom, scaled 0.7 or 0.8 (part1.py:1894, 3272, 3961; part2.py:173) |
| `to_corner(UP+LEFT)` | 20 | The current input image or the running word (part1.py:1083; part2.py:181, 1016) |
| `to_corner(UP+RIGHT)` | 13 | Secondary formula or counter (part1.py:3131, 3985; part2.py:2807; part3.py:2361) |
| `to_corner(DOWN+LEFT)` | 13 | Pi creature, or the computational graph (part3.py:2524) |
| `set_width(FRAME_WIDTH - 1)` | 10 | Full-width banner text and equations (part1.py:1800, 2960; part2.py:1954, 1968) |
| `set_height(FRAME_HEIGHT - 1)` | 5 | Full-height grids and lists (part1.py:588; part2.py:449) |
| `.scale(0.8)` | 19 | Secondary labels and captions |
| `.scale(0.7)` | 14 | Tertiary labels (part2.py:2163 `text_scale_value`) |
| `.scale(1.5)` | 14 | Titles and single big symbols |
| `.scale(2)` | 18 | Brackets, equals and plus signs between images, headline words |
| `add_background_rectangle` | 15 | Text placed over plots or planes (part2.py:1480, 1827, 1860, 2448) |
| `shift_onto_screen` | 5 | Safety after `next_to` near an edge (part1.py:799; part3.py:140) |

Composition patterns:

1. Diagram low and left, text high. The network is scaled to a height of about
   4 to 5 units and pushed to the bottom or left edge; the input image sits to
   its upper left; questions and formulas take the top strip
   (part1.py:1893-1896, 2208-2225; part2.py:172-182; part3.py:79-82).
2. Words point at things. A caption is placed with `next_to(rect, UP)` and an
   `Arrow(words.get_bottom(), target)` connects it (part1.py:1465-1472,
   2215-2222, 3072-3079; part2.py:2335-2338, 2624-2631; part3.py:132-136).
3. Boxes name regions. `SurroundingRectangle` (75 uses, default `YELLOW`,
   `SMALL_BUFF`; ManimGL `shape_matchers.py:23-31`) groups the hidden layers,
   the output layer with its labels, a term in a formula, and is removed right
   after (part1.py:1296-1301, 1554; part3.py:2800-2814).
4. Split screens use a full-height `Line` at the center and place each half with
   `shift(FRAME_X_RADIUS * RIGHT / 2)` or `set_width(FRAME_X_RADIUS - 1)`
   (part2.py:1222-1228, 1233-1235).
5. Formula and diagram share the frame by provenance: symbols are introduced
   next to the objects they summarize (`a1_label.next_to(neuron, RIGHT)`,
   part1.py:3416-3418; `formula.next_to(neuron, RIGHT)`, part2.py:663;
   `formula.next_to(neuron, UP, MED_LARGE_BUFF, RIGHT)`, part3.py:2430) and
   only then move to the top corner (`rhs.to_corner(UP+RIGHT)`, part3.py:845).
6. Object budget. The MNIST drawing has 58 visible neurons and 672 edges before
   `remove_random_edges(0.7)` leaves about 200; a frame then adds one image,
   one caption, one formula. Large layers are collapsed to 16 circles, dots and
   a brace (part1.py:152-169). Small conceptual networks use `[8, 6, 6, 4]`
   (24 neurons), `[8, 6]` for the matrix scene (part1.py:3344), `[1, 1, 1, 1]`
   for the calculus (part3.py:2150), `[3, 3, 2]` for indices (part3.py:3642).
7. Inserted footage gets a `ScreenRectangle` of height 4.5 to 6 in the upper
   left with a title above it (part1.py:3930-3934; part2.py:58-62, 1930;
   part3.py:1834, 2085-2087).
8. Lists are `arrange(DOWN, aligned_edge=LEFT)` with `MED_LARGE_BUFF` or
   `LARGE_BUFF`, left-aligned at `to_edge(LEFT, buff=LARGE_BUFF)` (part2.py:102-113,
   1949-1955; part3.py:909-915).

## 5. Animation idioms

### 5.1 Which animations dominate

Combined counts across the three files (section 9 has the per-file table):
`Write` 169, `FadeIn` 150, `FadeOut` 141, `ShowCreation` 130, `LaggedStartMap`
127, `ReplacementTransform` 117, `MoveToTarget` 77 (with `generate_target` 67),
`Transform` 52, `GrowArrow` 42, `ApplyMethod` 28, `DecimalNumber` 27,
`ChangingDecimal` 23, `Animation` 23, `Indicate` 21, `GrowFromCenter` 21,
`ShowCreationThenDestruction` 19, `UpdateFromFunc` 16, `DrawBorderThenFill`
12, `Blink` 11, `GrowFromPoint` 8, `ApplyFunction` 9, `ShowPassingFlash` 2,
`UpdateFromAlphaFunc` 2, `FocusOn` 2, `Rotate` 2, `Swap` 1.

The ManimGL shorthand `self.play(mob.method, arg, ...)` (an implicit
`ApplyMethod`) is everywhere, for example `self.play(randy.change, "pondering")`
(part1.py:366) and `self.play(network_mob.scale, 0.8, network_mob.to_edge,
DOWN)` (1456-1459). ManimCE spells this `mob.animate.method(arg)`.

### 5.2 Timing values

| Parameter | Distribution | Reading |
|---|---|---|
| `run_time` | 1: 104, 2: 71, 3: 26, 1.5: 17, 4: 9, 5: 3, 12: 2, 8: 1, 0.5: 1, 0.2: 1 | Default 1 s (`animation.py:19`); 2 s for writes and transforms that carry meaning; 3 to 5 s for reveals of many parts or slow sweeps; 12 s for a graph drawn while narrating (part2.py:3659, 3666) |
| `lag_ratio` | 0.5: 33, 0.7: 11, 0.3: 6, 0.4: 3, 0.2: 3, 0: 3, 0.8: 2, 0.6: 1 | `LaggedStartMap` defaults to 0.05 (`composition.py:24`) and `run_time=2`; the author overrides to 0.5 so successive parts overlap by half, and uses 0.7 to 0.8 for edge flashes that should read one at a time (part1.py:3622-3627; part3.py:1013) |
| `rate_func` | `there_and_back` 27, `wiggle` 22, `linear` 5, custom lambdas 6, `squish_rate_func(smooth, a, 1)` 2, `running_start` 1 | `there_and_back` for "nudge and return" (part3.py:2748-2756), `wiggle` for "this is adjustable" (part1.py:2421-2426; part2.py:308-312), `linear` for data-driven draws and propagation, `squish_rate_func` to delay one animation inside a group (part1.py:4004; part3.py:1587), a plateau function for a label that appears, holds and leaves (part2.py:2683-2690) |
| `path_arc` | pi/2: 7, pi/3: 2, pi/6 and -pi/6, pi, -2pi/3, -0.7pi | Curved paths for things that hop (image between layers part3.py:598-607), reorder (shuffle part3.py:1900-1906), or enter from the side (arrow part2.py:3104-3109) |

### 5.3 Transitions between ideas

- `ReplacementTransform(source.copy(), target)` is the signature move for "this
  symbol is that object": edges become `w` terms (part3.py:864, 2443-2446,
  2201-2235), neurons become `a` labels (part1.py:2457-2470; part3.py:871-874),
  a matrix, a column and a bias column become the bold `W`, `a`, `b` of the
  final formula (part1.py:3833-3857), a boxed row and column become a `?`
  result entry (part1.py:3666-3673), brace labels become equation terms
  (part1.py:1097-1103). 117 uses.
- `Transform(mob, mob_variant)` is for in-place state change where identity
  persists: a layer into its activated copy (part1.py:310), a word into a
  reworded copy (part3.py:1217), a number line into its sigmoid image
  (part1.py:2696-2713).
- `FadeOut` of a list via `*list(map(FadeOut, [...]))` clears a sub-scene in one
  beat (17 uses, e.g. part1.py:979-984, 3863-3870; part3.py:3085-3089), often
  with `LaggedStartMap(FadeOut, group)` for a staggered clear (part3.py:1095-1101).
- `save_state` and `restore` (48 and 57 uses) return the frame to a known
  layout after a digression (part1.py:1136-1140, 1163-1168; part3.py:2358-2367,
  3011-3019).
- `generate_target` plus `MoveToTarget` choreographs several objects at once
  (part1.py:1263-1270, 1646-1651; part3.py:626-668), with `generate_target(use_deepcopy=True)`
  when children move independently (part1.py:4266; part2.py:3194).
- `Transform(group, VectorizedPoint(center), remover=True)` collapses many
  objects into one point (part1.py:1423-1428; part2.py:2071-2075; part3.py:316-321).
- Instant setup uses `Transform(a, b).update(1)` instead of playing (13 uses,
  part1.py:2056-2064, 2815-2818, 3968-3971; part3.py:2958-2961).
- `remover=True` marks a transient mover so it vanishes after moving (14 uses,
  part1.py:359, 834; part2.py:203, 687).

### 5.4 Emphasis and release

| Effect | Recipe | Evidence |
|---|---|---|
| Signal flow | Copy an edge group, `set_stroke(YELLOW, 1.5x width)`, `ShowCreationThenDestruction(copy, lag_ratio=0.5)` | part1.py:238-248, 2012-2019; part2.py:203-209, 681-686 |
| Point at a term | `SurroundingRectangle` shown with `ShowCreation`, later `FadeOut` or `ReplacementTransform` into the next rectangle | part1.py:1557-1560, 3615-3628; part3.py:2800-2835 |
| Pulse | `Indicate` (default `scale_factor` 1.2, `YELLOW`, `there_and_back`; ManimGL `indication.py:74-84`), often inside `LaggedStartMap` over the parts of a formula | part1.py:1355-1361, 3540-3544; part3.py:338-342, 2238-2242 |
| Jiggle | `rate_func=wiggle` on a shift, rotate or `set_stroke` | part1.py:2421-2426; part2.py:2558-2563; part3.py:276-283, 3163-3167 |
| Nudge and return | `shift(MED_SMALL_BUFF*DOWN, rate_func=there_and_back, lag_ratio=0.5)` on each term class in turn | part3.py:886-892, 963-967 |
| Negate | `Cross(mob)` then `fade` the crossed thing | part1.py:466, 4030-4040, 4384 |
| Flash an outline | `ShowPassingFlash(outline, time_width=0.5, run_time=2)` | part1.py:541-547, 971-976 |
| Keep on top | `Animation(mob)` inside a `play` so a mobject re-renders above others | part1.py:2259, 3372-3375, 3466; part2.py:979 |
| Dim the rest | `fade(0.8)` or `set_stroke(None, 0.25)` on everything except the focus, restored later | part1.py:3360-3375; part2.py:3062-3074; part3.py:2244-2256 |
| Mask | Black-filled rectangle over a region, or a punchline colored `BLACK` until revealed | part1.py:3277-3283; part2.py:2976, 2992; part3.py:1307-1311 |
| Hold the eye | A dot or `FocusOn` before a cluster is indicated | part1.py:3538; part3.py:1457 |

### 5.5 Updaters and live values

- `ChangingDecimal(decimal, lambda a: ...)` with a parallel `UpdateFromFunc` that
  flips text color at opacity 0.8 (part1.py:1142-1153; part3.py:744-756).
- `UpdateFromFunc` chains keep dependent objects consistent during one play:
  moving `w` drags the vertical line, the dot, and in chapter 4 the `z`, `a`
  and `C` dots on their number lines (part2.py:1588-1600; part3.py:2700-2756).
- `Mobject.add_updater` for physics-like motion: balls rolling down the cost
  curve with slope-proportional steps (part2.py:555-573, 1720-1740).
- `MaintainPositionRelativeTo(label, mover)` for a label that rides along
  (part1.py:602, 3501; part2.py:1653, 1680).
- `ContinualEdgeUpdate` (section 2.5) for ambient motion while the narration
  talks (`wait(10)` after adding it, part1.py:3202-3203, 3258, 3316).

### 5.6 ManimCE translation notes (names checked in the 0.22.0 clone)

| ManimGL idiom in the series | ManimCE equivalent | Status |
|---|---|---|
| `OldTex`, `OldTexText` | `MathTex`, `Tex` (`manim/mobject/text/tex_mobject.py`) | present; `set_color_by_tex`, `set_color_by_tex_to_color_map`, `get_part_by_tex` exist (tex_mobject.py:543-585) |
| `ShowCreation` | `Create` (`manim/animation/creation.py:140`) | renamed |
| `ShowCreationThenDestruction` | none; use `ShowPassingFlash(copy, time_width=...)` (`indication.py:274`) or `Succession(Create, Uncreate)` | missing in CE |
| `self.play(mob.method, args)` | `mob.animate.method(args)` (`mobject.py:313`) | changed |
| `CONFIG = {...}` | constructor keyword arguments or class attributes | changed |
| `GraphScene` | removed; use `Axes` and `axes.plot`, `axes.get_graph_label`, `axes.input_to_graph_point` | missing in CE |
| `LaggedStartMap(FadeIn, group, lag_ratio=0.5)` | same name (`composition.py`), same default `lag_ratio` 0.05 (composition.py:27) | present |
| `Indicate`, `FocusOn`, `Flash`, `Wiggle` (for `rate_func=wiggle` moves) | present in `indication.py` | present |
| `GrowArrow`, `GrowFromCenter`, `GrowFromPoint`, `DrawBorderThenFill`, `Write` | present | present |
| `ChangingDecimal`, `UpdateFromFunc`, `UpdateFromAlphaFunc`, `MaintainPositionRelativeTo` | present (`animation/numbers.py`, `animation/updaters/update.py`); idiomatic CE uses `ValueTracker` and `always_redraw` | present |
| `Brace.get_text`, `Brace.get_tex` | present (`brace.py:157, 176`) plus `BraceLabel` | present |
| `SurroundingRectangle`, `BackgroundRectangle`, `Cross`, `Underline` | present (`geometry/shape_matchers.py`) | present |
| `DecimalNumber`, `Integer`, `Matrix`, `DecimalMatrix`, `BulletedList`, `Title` | present | present |
| `ScreenRectangle`, `VideoIcon` | `ScreenRectangle` present (`frame.py`); `VideoIcon` is ManimGL only | partial |
| Pi creatures, `TeacherStudentsScene`, `Eyes` | not in CE; they live in `custom/` and are not needed for the target skill | absent |
| `force_skipping` / `revert_to_original_skipping_status` | `self.next_section(..., skip_animations=True)` and `--from_animation_number` | present (grep in `scene/scene.py`) |
| `ContinualAnimation` | `add_updater` (already used by `ContinualEdgeUpdate`) | changed |
| `rate_func=wiggle`, `there_and_back`, `running_start`, `squish_rate_func` | same names in `manim/utils/rate_functions.py` | present |

## 6. Pacing and narrative structure

### 6.1 Chapter arcs as sequenced by the scenes

Chapter 1 (`part1.py`, read top to bottom): a concrete puzzle (recognize 3s
drawn differently, 336-525), the brain (527), what a program would need (552),
a plan that previews the whole network and even the matrix formula (619-782),
a working network on real digits before anything is explained (784-845), the
name taken apart (929-1034), a neuron is a number (990-1034), pixels become the
input layer and activations get their name (1036-1335), the hidden-layer choice
admitted as arbitrary (1337-1398), a hoped-for hierarchy of patterns macro then
micro (1488-2088) with the honest flag "Does the network actually do this?
We'll get back to this" (2032-2047), then the mechanics: weights (2237), the
need to squish (2619), sigmoid (2717), bias (2780), the parameter count 13,002
and "learning = finding the right weights and biases" (3017-3234), failure and
black-box warnings (3261-3332), the matrix formula built from the pieces
(3334-3887), the reframe "a neuron is a function, the network is a function"
(3947-4129), and the hand-off (4141-4298). The ReLU footnote repeats the
pattern in miniature (4368-4544).

Chapter 2 (`part2.py`): recap and plan (57-140), training shown before it is
defined (142-321), data (330-503), a joke that frames "learning" as calculus
(505-539), minima on a graph (541-574), the cost defined from the numbers on
screen (585-1121), the cost as a function of 13,002 inputs (1214-1410), one
variable (1440-1808), two variables and the gradient (1819-1924), the gradient
read non-spatially as "which weights matter" (1974-2316), nudging (2576-2700),
performance (2772-2996), what the weights actually learned versus the chapter-1
hope (2998-3262), the research aside on memorization (3489-3698).

Chapter 3 and 4 (`part3.py`): plan with four re-inserted recaps (5-53), the
gradient components interpreted (55-348), the notation shock (350-416), the
average over examples (423-538), the intuitive walkthrough on one example
(545-1388), the Hebbian aside with disclaimers (1390-1461), aggregating
requests into the gradient (1463-1831), SGD and mini-batches (1848-2010), the
code and calculus hand-off (2018-2092), the 1-1-1-1 derivation (2094-3621),
generalization to indices (3641-4194), the stacked equations as a recap (4223).

### 6.2 What appears before any formula

- Chapter 1 shows a working classifier (784-845) and the "neuron holds a number"
  idea (990-1034) roughly 1900 lines before the first weighted sum is written
  (2435). The only earlier formula is the one-line preview in `LayOutPlan`
  (686-700), which the plan then puts away (`FadeOut(self.equation)`, 727).
- Chapter 2 writes the cost as `(0.00 - 0.00)^2 + ...` using the decimals that
  are already on screen (857-915) before any `C(w)` symbol (1462-1494), and the
  gradient as an arrow on a plane (1876-1923) before `-nabla C` as a column of
  numbers (1974-2082).
- Chapter 3 spends the whole intuitive walkthrough (545-1388) with only one
  formula (the activation of one neuron, 824-900), and chapter 4 brings each
  derivative to its formula physically before differentiating
  (`cost_equation.next_to(dC_da.rhs, DOWN, ...)` then restore, 3014-3025).

### 6.3 How recaps are done

- Opening and closing tags: `<Recap>` turning into `</Recap>` (part2.py:127-140)
  and `<Stochastic gradient descent>` (part3.py:1848-1866).
- Plan lists where the current item stays bright and the rest dim to 0.5
  (`ShowPlan`, part2.py:116-123; `BulletedList.fade_all_but`, part3.py:30-32).
- Re-rendered earlier scenes marked with `TODOStub` messages (part3.py:35-53).
- A screen rectangle with "I assume you've watched this" (part2.py:57-89).
- Carried-over objects: `ShowAveragingCost` rebuilds chapter 2's cost picture
  (part3.py:437-456) before `WalkThroughTwoExample` modifies it.
- End-of-chapter stacking: all chain-rule equations braced into `nabla C`
  (part3.py:4223-4285); "Learning = Finding the right weights and biases"
  (part1.py:3191-3194).

### 6.4 Beat structure and `wait()`

- 795 `self.play` calls and 423 `self.wait` calls across the three files: about
  one pause every two animations. 286 waits are the bare 1 s default, 84 are 2 s,
  12 are 3 s. The rhythm inside a step is `play`, `wait()`, `play`, `wait()`,
  with a `wait(2)` closing the step (part1.py:1101-1104; part3.py:2316-2318).
- Long holds (5 to 10 s) occur where narration or inserted footage carries the
  moment: wrappers and sponsor frames (part1.py:3941, 4560; part2.py:1940;
  part3.py:1845), ambient `ContinualEdgeUpdate` shots (part1.py:3203, 3258,
  3316, 4296), dots rolling downhill (part2.py:574), and reaction shots
  (`wait(7)`, part1.py:3332).
- Sub-second waits drive montages that say "many": 0.5 s per alternate three
  (part1.py:415), 0.2 s per flashed digit (1750, 4181), a shrinking schedule
  0.5, 0.25, 0.125, 0.1 s over training examples (part2.py:1015-1020), 1/30 s
  per scrolled example (409), 1/120 s per MNIST pair (430), 0.1 s per test
  digit with 0.5 s extra on mistakes (2773-2776, 2884-2886), 1/15 s per example
  (part3.py:431).
- Narration is not in the code. There are no audio calls; timing is set by
  `wait` and `run_time`, and the author assembled scene renders against a
  recorded voice-over in an editor (inferred from the stubs and the per-scene
  structure; unverified against any external statement).

### 6.5 How long an idea gets

Each step method is one idea and runs 3 to 8 plays with a wait after most of
them; a spine scene has 5 to 13 steps (31 in `SimplestNetworkExample`). Between
spine scenes, a reaction or question scene of 1 to 3 plays and a 2 to 5 s hold
resets attention (`DiscussChoiceForHiddenLayers`, `NotSciFi`,
`IsntThatOverSimplified`). Questions are planted before answers: 14
`student_says`, question captions with arrows (part1.py:1462-1486, 2209-2225;
part2.py:3129-3135; part3.py:129-136), and explicit deferrals ("We'll get back
to this", part1.py:2036-2038; "(Backpropagation be the next video)",
part2.py:323-328).

## 7. Pi creatures and text

### 7.1 Characters

Mode frequencies across the three files: `pondering` 21, `raise_right_hand` 18,
`hooray` 11, `sassy` 10, `happy` 10, `confused` 10, `thinking` 9, `hesitant` 6,
`sad` 5, `angry` 5, `plain` 4, `horrified` 4, `guilty` 4, `surprised` 3,
`shruggie` 3, `raise_left_hand` 3, `pleading` 3, `maybe` 3, `erm` 3,
`concerned_musician` 3, `speaking` 2, `tired` 1.

Usage patterns:

- The teacher presents with `raise_right_hand` while students go `pondering`
  (part1.py:648-652, 772-776; part2.py:71-80; part3.py:1837-1842).
- Students voice the viewer's objections through `student_says` (14 uses):
  "Why the layers?" (part1.py:703), "Why 2 layers?" and "Why 16?" (1378, 1388),
  "recognizing loops is just as hard!" (1757), "Should we be worried?"
  (part2.py:516), "13,002-dimensional nudge?" (2145), "I can't follow that code"
  (part3.py:2064), "Isn't that over-simplified?" (3626). The teacher answers
  with `teacher_says` (17 uses) in `hooray`, `hesitant`, `guilty` or `surprised`
  modes depending on whether the answer is a payoff, a caveat or a confession
  (part1.py:922-925; part2.py:2976-2983, 3437-3440; part3.py:3634-3638).
- Complexity is acknowledged with `confused`, `horrified`, `pleading`
  (part1.py:3895; part2.py:2149; part3.py:393-396, 2021-2024, 3121-3124) and
  hedges with `shruggie`, `maybe`, `guilty` (part1.py:1375, 886, 1762).
- The network itself gets eyes and a speech bubble so it can be yelled at,
  look sad, or answer "Looks like a 5 to me!" (part2.py:1123-1202, 3193-3225,
  3228-3262; part3.py:1760-1769).
- Characters are placed in a lower corner, scaled 0.6 to 0.8 when sharing the
  frame with content (part1.py:3238-3240; part3.py:138-141, 1033-1035,
  3118-3122), and `Blink` (11 uses) fills holds.

### 7.2 Text and formulas

- `OldTexText` (191 uses) for words, `OldTex` (157) for math; words slightly
  outnumber formulas. Default font size is 48 (ManimGL
  `mobject/svg/old_tex_mobject.py:32`); the series scales rather than sets
  sizes: 0.7 to 0.8 for captions and secondary formulas (`derivative_scale_val`
  0.85, part3.py:2100; chain rule 0.8, 4169), 1.5 to 2 for titles and banner
  words (part1.py:893, 905; part2.py:92, 179), 3 for the thumbnail title
  (part1.py:4597), and `set_width(FRAME_WIDTH - 1)` for one-line banners.
- Multi-line text uses `\\\\` inside one string (18 uses), e.g. "Only activate
  meaningfully \\\\ when" (part1.py:2874-2876).
- Newly introduced terms are set in LaTeX quotes: "Activation" (part1.py:1158),
  "Hidden layers" (1297), "bias" (2896), "Little edge" layer (1961), "cost"
  (part2.py:835), "Gradient" (1888), "Mini-batches" (part3.py:1919).
- Formulas are built from isolated substrings so parts can be colored and moved
  independently: `OldTex("\\textbf{a}_{l+1}", "=", "\\sigma(", "W_l", ...)`
  (part1.py:686-696), the weighted sum as alternating `w_d`, `a_d`, `+` pieces
  (part1.py:2620-2627; part2.py:639-646), `get_parts_by_tex("w_")` to grab a
  class of terms (part2.py:647-648; part3.py:832-838).
- Numbers are shown as `DecimalNumber` with 1 to 4 decimal places chosen for
  the job: 1 inside neurons (part1.py:1118; part3.py:674), 2 by default, 3 for
  the accuracy readout (part2.py:2777-2779), 4 for squared-error terms (952).
- Braces label sizes and groups with `Brace(...).get_text(...)` or `get_tex`
  (19 uses): "28px" (part1.py:350-354), "784" on the input layer (164-169),
  "Weights and biases" versus "Single input" (part2.py:1471-1476), "Cost of one
  example" (part3.py:452-454), "Sum over layer L" (4029-4030).

## 8. The moves that make it good

1. Start with a working thing, not a definition. A pretrained network
   classifies real test digits (`PreviewMNistNetwork`, part1.py:784-845) and
   trains on real data (`PreviewLearning.show_training`, part2.py:184-192)
   before any term is defined; the network numbers are the true activations
   (`activate_layers`, part1.py:225-228).
2. Preview the destination, then hide it. The chapter-1 plan flashes the final
   matrix equation (part1.py:686-700) and fades it (727); chapter 3's plan
   names the three movements (part3.py:11-15). The viewer knows where the road
   leads before walking it.
3. Zoom to one unit and build the formula from its parts. One neuron is pulled
   out, the rest faded (`zoom_in_on_one_neuron`, part1.py:2253-2270;
   `isolate_one_neuron`, part2.py:605-626; `fade_many_neurons`, 3360-3375;
   `focus_on_one_neuron`, part3.py:782-822), and its weighted sum appears term
   by term with each term flying out of the object it stands for
   (part1.py:2457-2491; part3.py:855-884).
4. Numbers before symbols. Activations are decimals inside circles
   (part1.py:1112-1172); the cost is `(0.00 - 0.00)^2` sums of on-screen
   decimals that update as the output changes (part2.py:857-1004); the gradient
   is a column of signed decimals before it is `nabla C` (2157-2316); the
   chain rule is first felt by dragging a dot and watching three other dots
   move (part3.py:2700-2778).
5. Provenance by transformation. `ReplacementTransform(x.copy(), symbol)` ties
   every symbol to a picture: edges to `w`, neurons to `a`, matrix to `W`,
   column to `a`, bias column to `b`, big parentheses to `sigma`
   (part1.py:3833-3857), a boxed row and column to one output entry
   (3666-3673), the `> 10` threshold to the `-10` bias (2903-2908).
6. Say what you do not know. "Upper loop neuron...maybe..." (part1.py:1674),
   "Does the network actually do this? We'll get back to this" (2032-2047),
   "Well... not at all!" when the learned weights look like noise
   (part2.py:2973-2996), "Definitely not a neuroscientist" and "No claims
   here..." (part3.py:1398-1461), "...theoretically" (part3.py:490-496).
7. Give the adjustable things a tremor. `rate_func=wiggle` on edges and symbols
   marks "these are the knobs" (part1.py:2421-2426; part2.py:303-312,
   718-726; part3.py:276-283, 2232-2236, 3861-3868), and a nudge-and-return
   shift marks "this is what we vary" (part3.py:886-892, 2748-2756).
8. Light the path, then release. Yellow `ShowCreationThenDestruction` flashes
   trace signal flow, the path from a weight to the cost, or the paths from one
   neuron to the sum (part1.py:238-248; part3.py:2534-2536, 3340-3348,
   4036-4044); rectangles and indications are removed before the next idea
   (part1.py:1326-1328; part3.py:2832-2835).
9. Keep one consistent color per concept across words, symbols, arrows and
   diagrams, applied by substring (`set_color_by_tex_to_color_map`,
   part1.py:3805-3810; part3.py:376-384, 3314-3318, 4273-4278). The chapter-1
   drift (green weights, blue bias) is corrected from chapter 2 on.
10. Control the object budget. 784 inputs become 16 circles, dots and a brace
    (part1.py:152-169); 70 percent of edges are removed in overview shots
    (316-322, 790); the calculus is done on a 1-1-1-1 network (part3.py:2141-2199)
    and only then on 3-3-2 (3641).
11. Montage conveys scale. Rapid cycling at 0.03 to 0.5 s per item for data,
    examples, training pairs and mini-batches (part2.py:401-412, 1006-1049,
    2847-2896; part3.py:466-470, 3266-3284).
12. Characters stage the viewer's reactions and questions and give permission
    to be confused (section 7.1); the network gets eyes so failure has a face
    (part2.py:1123-1202, 3228-3262).
13. Recap by carrying the picture forward, not by restating: the cost picture
    is rebuilt before being modified (part3.py:437-456), the plan dims the done
    items (part2.py:116-123), the chapter ends by stacking what was built into
    one object (part1.py:3171-3194; part3.py:4223-4285).
14. Determinism. `np.random.seed` and `random.seed` fix every random layout
    (part2.py:2320, 3094; part3.py:548-550, 1877-1879, 2137-2139), so re-renders
    match the recorded narration.
15. Return to the saved layout after each digression (`save_state` and
    `restore`, 105 uses together) so the frame never accumulates clutter; mass
    `FadeOut` clears a sub-scene in one beat before the next begins.
16. Place captions next to their referent and connect them with an arrow or a
    brace rather than listing them elsewhere (section 4, patterns 2 and 3).

## 9. Counts table

Per-file `grep -oE '\b(Name)\b' | sort | uniq -c` over `part1.py`, `part2.py`,
`part3.py`. Word boundaries keep `Transform` from matching
`ReplacementTransform` and `copy` from matching `deepcopy`.

| Name | part1 | part2 | part3 | Total |
|---|---|---|---|---|
| `VGroup` | 162 | 112 | 216 | 490 |
| `wait` | 155 | 111 | 157 | 423 |
| `next_to` | 123 | 106 | 110 | 339 |
| `run_time` | 84 | 77 | 84 | 245 |
| `OldTexText` | 72 | 75 | 44 | 191 |
| `copy` | 62 | 35 | 88 | 185 |
| `Write` | 62 | 38 | 69 | 169 |
| `OldTex` | 52 | 36 | 69 | 157 |
| `FadeIn` | 70 | 45 | 35 | 150 |
| `FadeOut` | 51 | 30 | 60 | 141 |
| `shift` | 42 | 40 | 58 | 140 |
| `scale` | 40 | 46 | 54 | 140 |
| `ShowCreation` | 46 | 32 | 52 | 130 |
| `LaggedStartMap` | 35 | 28 | 64 | 127 |
| `move_to` | 49 | 35 | 43 | 127 |
| `ReplacementTransform` | 39 | 18 | 60 | 117 |
| `to_edge` | 42 | 42 | 30 | 114 |
| `MoveToTarget` | 35 | 16 | 26 | 77 |
| `SurroundingRectangle` | 25 | 16 | 34 | 75 |
| `generate_target` | 31 | 15 | 21 | 67 |
| `rate_func` | 13 | 11 | 42 | 66 |
| `lag_ratio` | 29 | 15 | 19 | 63 |
| `Arrow` | 25 | 20 | 18 | 63 |
| `set_height` | 33 | 21 | 7 | 61 |
| `arrange` | 24 | 18 | 18 | 60 |
| `restore` | 24 | 5 | 28 | 57 |
| `to_corner` | 17 | 20 | 20 | 57 |
| `Transform` | 27 | 11 | 14 | 52 |
| `save_state` | 17 | 7 | 24 | 48 |
| `GrowArrow` | 9 | 15 | 18 | 42 |
| `TeacherStudentsScene` | 9 | 11 | 9 | 29 |
| `ApplyMethod` | 6 | 8 | 14 | 28 |
| `DecimalNumber` | 7 | 12 | 8 | 27 |
| `there_and_back` | 7 | 2 | 18 | 27 |
| `Group` | 10 | 12 | 4 | 26 |
| `Brace` | 6 | 7 | 12 | 25 |
| `Line` | 8 | 7 | 10 | 25 |
| `wiggle` | 1 | 3 | 21 | 25 |
| `ChangingDecimal` | 4 | 9 | 10 | 23 |
| `Animation` | 10 | 11 | 2 | 23 |
| `set_width` | 10 | 6 | 5 | 21 |
| `Indicate` | 4 | 1 | 16 | 21 |
| `GrowFromCenter` | 4 | 8 | 9 | 21 |
| `ShowCreationThenDestruction` | 6 | 2 | 11 | 19 |
| `get_part_by_tex` | 2 | 8 | 9 | 19 |
| `teacher_says` | 3 | 8 | 6 | 17 |
| `UpdateFromFunc` | 2 | 7 | 7 | 16 |
| `play_student_changes` | 5 | 6 | 5 | 16 |
| `PiCreatureScene` | 8 | 5 | 3 | 16 |
| `replace` | 16 | 6 | 8 | 30 |
| `student_says` | 7 | 5 | 2 | 14 |
| `set_color_by_tex` | 4 | 5 | 4 | 13 |
| `DrawBorderThenFill` | 5 | 7 | 0 | 12 |
| `Vector` | 0 | 6 | 6 | 12 |
| `get_parts_by_tex` | 0 | 3 | 9 | 12 |
| `linear` | 4 | 3 | 0 | 7 |
| `Circle` | 7 | 2 | 2 | 11 |
| `Blink` | 6 | 1 | 4 | 11 |
| `ImageMobject` | 10 | 1 | 0 | 11 |
| `set_color_by_tex_to_color_map` | 2 | 0 | 8 | 10 |
| `ScreenRectangle` | 2 | 4 | 4 | 10 |
| `deepcopy` | 5 | 2 | 3 | 10 |
| `change_students` | 3 | 3 | 4 | 10 |
| `ContinualEdgeUpdate` | 7 | 2 | 1 | 10 |
| `ApplyFunction` | 0 | 2 | 7 | 9 |
| `align_to` | 2 | 0 | 6 | 8 |
| `GrowFromPoint` | 8 | 0 | 0 | 8 |
| `Dot` | 0 | 6 | 2 | 8 |
| `smooth` | 3 | 4 | 1 | 8 |
| `shift_onto_screen` | 2 | 1 | 2 | 5 |
| `Randolph` | 4 | 2 | 2 | 8 |
| `add_updater` | 1 | 3 | 0 | 4 |
| `GraphScene` | 1 | 3 | 0 | 4 |
| `Cross` | 3 | 1 | 0 | 4 |
| `RemovePiCreatureBubble` | 3 | 1 | 0 | 4 |
| `Mortimer` | 2 | 0 | 1 | 3 |
| `NumberPlane` | 0 | 3 | 0 | 3 |
| `MaintainPositionRelativeTo` | 2 | 3 | 0 | 5 |
| `arrange_in_grid` | 1 | 2 | 1 | 4 |
| `squish_rate_func` | 1 | 0 | 1 | 2 |
| `ShowPassingFlash` | 2 | 0 | 0 | 2 |
| `UpdateFromAlphaFunc` | 1 | 0 | 1 | 2 |
| `FocusOn` | 1 | 0 | 1 | 2 |
| `NumberLine` | 1 | 0 | 1 | 2 |
| `SVGMobject` | 2 | 0 | 1 | 3 |
| `running_start` | 1 | 0 | 0 | 1 |
| `BulletedList` | 0 | 0 | 1 | 1 |

Other counted facts: `self.play(` 275 / 189 / 331 (795 total); `self.wait(`
155 / 111 / 157 (423); `def construct` 45 / 49 / 26 (120); `force_skipping` 4 /
1 / 1; `revert_to_original_skipping_status` 7 / 2 / 1; `set_variables_as_attrs`
0 / 1 / 25; `remover = True` 5 / 6 / 3; `.update(1)` 7 / 4 / 2; `random.seed`
0 / 4 / 10; `map(FadeOut` 7 / 2 / 8; `add_background_rectangle` 2 / 12 / 1;
`load_data_wrapper()` 3 / 7 / 3; `get_organized_images()` 10 / 5 / 2;
`Eyes(` 0 / 3 / 1; `ExternallyAnimatedScene` or `TODOStub` 1 / 8 / 8.

Color constants: `YELLOW` 103, `WHITE` 101, `BLUE` 78, `RED` 70, `GREEN` 44,
`BLACK` 27, `MAROON_B` 16, `GREY_B` 12, `TEAL` 3, `BLUE_C` 2, `BLUE_B` 2,
`RED_B` 1, `PURPLE` 1, `PINK` 1, `GREEN_B` 1, `BLUE_E` 1, `BLUE_D` 1.

Direct `set_color(X)` calls on text and groups: `YELLOW` 53, `RED` 25, `BLUE`
26, `GREEN` 15, `WHITE` 14, `MAROON_B` 7, `BLACK` 4, `GREY_B` 1.

## Appendix A. Reproducing the counts

```bash
cd /home/user/3b1b/videos/_2017/nn
for f in part1.py part2.py part3.py; do
  echo "== $f"
  grep -oE '\b(Write|FadeIn|FadeOut|ShowCreation|ReplacementTransform|Transform|MoveToTarget|LaggedStartMap|Indicate|GrowArrow|ChangingDecimal|UpdateFromFunc|SurroundingRectangle|OldTex|OldTexText|VGroup|wait|run_time|lag_ratio|rate_func)\b' "$f" \
    | sort | uniq -c | sort -rn
done
grep -ohE 'self\.wait\([^)]*\)' part1.py part2.py part3.py | sort | uniq -c | sort -rn
grep -ohE 'run_time *= *[0-9.]+' part1.py part2.py part3.py | sed 's/ //g' | sort | uniq -c | sort -rn
grep -ohE 'lag_ratio *= *[0-9.]+' part1.py part2.py part3.py | sed 's/ //g' | sort | uniq -c | sort -rn
grep -ohE 'rate_func *= *[A-Za-z_]+' part1.py part2.py part3.py | sort | uniq -c | sort -rn
```

The per-scene table in section 1 came from an `ast` walk over each module that,
for every top-level class, counted `self.play` and `self.wait` calls, summed
numeric `wait` arguments (bare `wait()` as 1.0) and numeric `run_time` keyword
values, and recorded `lineno` to `end_lineno`. The script lives at
`/tmp/claude-0/-home-user--agents/b713d8f3-7c52-540b-8252-65c41f426313/scratchpad/tools/scene_metrics.py`
and is run with `python3 -I scene_metrics.py part1.py part2.py part3.py`.

## Appendix B. ManimCE partial-render equivalents

The series relies on `force_skipping` to re-render only the step under
development. In the ManimCE 0.22.0 clone, `Scene.next_section(...,
skip_animations=False)` is defined at `manim/scene/scene.py:378-385`, and the
CLI options `from_animation_number` and `upto_animation_number` (flag `-n`) are
declared at `manim/_config/default.cfg:54-59`. A skill that renders iteratively
should use sections so a narration-synced scene can be re-rendered one section
at a time.

## Appendix C. Unverified items

- `TODOStub` and `PatreonThanks` definitions were not found anywhere in the
  videos clone by grep (outside the `_20xx` folders); their behaviour is
  inferred from use.
- The claim that ManimCE's named colors and buffer constants equal ManimGL's
  defaults was not checked against the CE clone's `constants.py` and
  `manim_colors.py`.
- Nothing about narration timing or the editing workflow is in the code; the
  statement that scenes are cut against a separately recorded voice-over is an
  inference from the stubs, the `wait` schedule and the absence of audio calls.
- `gradient.py`'s date and purpose could not be read from git history (the
  clone is shallow, one commit); its API vintage is inferred from the
  identifiers it uses.
- Line numbers in the ManimGL and ManimCE clones refer to the commit cloned on
  2026-10-25 and will drift.

