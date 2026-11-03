# Framework: thirty rules for a narrated lesson

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

Thirty rules in seven groups: narrative R01 to R07, voice R08 to R11, visual R12 to R17,
color R18 to R20, layout R21 to R23, timing R24 to R27 and honesty R28 to R30. Each rule
states what to do, why the corpus supports it, how the lesson.json fields apply it, what
checks it, where it holds, what a failing case looks like and the technique tags under which
the exemplar pack files its examples. Why cites analysis records by lesson slug and section
id, and the census.md and video.json files of the lessons it names; the citations resolve in
the manim-3b1b-corpus repository, not in the kit, and so does the section number in R24's
title, which names a section of the design spec kept there. A rule whose Check (storyboard)
line names storyboard_check.py has a PREDICATES entry that implements its Apply text;
nothing is parsed from this file at run time. The numbers of R08, R09 and R11 and the
palette of R19 are the kit constants R08_MAX_WORDS, R09_MINUTES_PER_QUESTION,
R11_FIRST_FORMULA_FRACTION and ROLE_COLORS.

R01 a working thing before any definition
Statement: open on something that visibly works, a machine running or a puzzle the viewer
  can try, before any term, definition or formula is given.
Why: the strongest openings run the finished machine on real input before naming any part of
  it (analyses backpropagation s01; mini-llm s01; mlp s01), or pose a puzzle the viewer
  solves at a glance, a messy handwritten digit read at once (neural-networks s01).
Apply: the lesson's first beat lists hook in moves.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the first beat's frames show the working thing in motion and no definition
  or formula.
Scope: the first beat of every generated lesson. The rule is prescriptive: several corpus
  openings start on a series pointer, a plan or a recap instead (gradient-descent s01,
  backpropagation-calculus s01), and a generated lesson does not copy them.
Fails: a first beat that shows the lesson title and reads out what a neuron is.
Exemplars: working-thing-first.

R02 the destination is previewed, then hidden until earned
Statement: show the finished picture briefly near the start, take it away, and bring it back
  only when every part of it has been built.
Why: the full layer equation, the attention grid and the list of levers each appear early,
  leave, and return assembled from pieces the lesson made (analyses neural-networks s03,
  s25; attention s08, s16; backpropagation s01, s09).
Apply: an early beat's visual shows the end state and a following beat removes it; the beat
  that brings it back builds it from objects that beats in between list in introduces. The
  preview beat lists no symbol_introduced and no formula in moves; the symbols are
  introduced in the beats that earn them, so R07 and R11 judge the build, not the preview.
Check (storyboard): none.
Check (frames): the preview beat's last frame no longer shows the end state, and the payoff
  beat's mark frame shows it built from objects drawn in between.
Scope: lessons with one destination picture; a lesson of separate facts may skip the
  preview.
Fails: the finished formula sits on screen from the first scene to the last, or first
  appears in the closing scene.
Exemplars: preview-then-hide.

R03 a question is planted before its answer and held across at least one beat
Statement: ask the question in one beat and answer it in a later one, so the viewer carries
  it for at least a beat.
Why: questions are put on screen or into words and held for a beat or a whole section before
  the answer lands (analyses neural-networks s17; attention s12; gradient-descent s11;
  mini-llm s09).
Apply: a beat whose narration ends in a question mark is not the lesson's last beat, and its
  introduces and symbol_introduced are empty.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the question beat's last frame shows what the question is about and no
  answer yet.
Scope: every spoken question, rhetorical ones included; a question shown with
  question_caption keeps the same order. The rule is prescriptive: some corpus questions are
  answered or set aside in the beat that asks them (attention s21 b01; mlp s08 b06, s18 b02,
  s27 b05), and a generated lesson does not copy them.
Fails: a beat that asks what the bias is for and introduces the bias in the same breath.
Exemplars: viewer-voice.

R04 one idea per scene, named in the scene title
Statement: give each scene one idea and name that idea in the scene title.
Why: short sections carry a single idea named by a title written beside the one picture it
  names (analyses neural-networks s19; backpropagation s14; gpt s22; mlp s20).
Apply: each scene's title names one idea, and the entries of introduces in that scene serve
  it; a second idea opens a new scene.
Check (storyboard): none.
Check (frames): the scene's frames carry one idea, and any title on screen matches the scene
  title.
Scope: every scene; a recap scene may revisit several ideas it names together. In the corpus
  one code class can span several sections (gradient-descent s05, s06), so the scene, not
  the class, is the unit. The rule is prescriptive: some corpus sections join two ideas
  (backpropagation-calculus s08, s12; mini-llm s07; attention s29), and a generated lesson
  gives each idea its own scene instead.
Fails: a scene titled for the weights that also introduces the bias and the sigmoid.
Exemplars: caption-next-to-referent.

R05 zoom to one unit before showing the crowd
Statement: work one unit, a neuron, a token or a column, all the way through, then show the
  same step across the crowd.
Why: one neuron, one query or one lane is worked through before the whole layer receives the
  same step (analyses neural-networks s26; attention s13; gpt s08; mlp s09).
Apply: the beat that introduces a per-unit step shows it on one unit with the rest dimmed
  (focus_and_dim or zoom_to), and a later beat applies it to all units (staggered).
Check (storyboard): none.
Check (frames): the step's first mark frame shows one unit isolated or enlarged, and the
  crowd receives the step only in a later beat. No rubric item scores R05, so the frame critic
  counts a lapse only where it also meets an item's anchor, under that item's rule ids.
Scope: steps that repeat over many units; a hook may show the whole machine running first.
  The rule is prescriptive: some corpus sections show the crowd before any single unit
  (mini-llm s10, s11; gpt s07, s20), and a generated lesson does not copy them.
Fails: a 64-cell score grid that fills all at once before any single cell is computed.
Exemplars: zoom-to-one-unit, one-then-all.

R06 the lesson's picture is carried into the recap
Statement: close by bringing back the lesson's own picture and restating the idea on it; the
  closing recap adds nothing new.
Why: recaps replay or rebuild the objects the lesson made, and a recap that opens on a text
  list goes on to the pictures (analyses backpropagation s19 b03 to b05; gpt s39 b02;
  mini-llm s12; attention s31).
Apply: the last scene has at least one beat whose moves include recap, and every such recap
  beat has empty introduces and symbol_introduced.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the recap beats' frames show objects first drawn earlier in the lesson, not
  a text list.
Scope: the last scene of every generated lesson. The rule is prescriptive: corpus videos
  often end on a sequel pointer, credits or a research aside after their recap
  (neural-networks s30, gradient-descent s27, s28), or recap in formulas alone with none of
  the lesson's pictures (backpropagation-calculus s15), and a generated lesson ends on a
  recap that carries its picture instead.
Fails: a last scene that recaps in bullet text and then introduces a new activation
  function.
Exemplars: carry-picture-forward.

R07 a quantity is shown as a number before its symbol; the symbol transforms from a copy of the number
Statement: show a quantity as a concrete number before its symbol, and let the symbol arrive
  by transforming a copy of that number or of the object that holds it.
Why: values sit on screen before letters name them, and large counts are copied up into the
  product that names them (analyses neural-networks s07, s20; attention s13; mlp s12).
Apply: every entry of a beat's symbol_introduced appears in the shows_value_of of a strictly
  earlier beat.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the introducing beat's mark frame still shows the source number, and the
  symbol sits where its copy landed.
Scope: scenes introducing notation; a recap may show a known symbol. The rule is
  prescriptive: some corpus derivations write the symbol before its value
  (backpropagation-calculus s02 b05, s06 b03; gradient-descent s18 b01), and a generated
  lesson does not copy them.
Fails: a first beat that writes a = sigma(Wx + b).
Exemplars: numbers-before-symbols, provenance-transform, parameter-count.

R08 a beat is 1 to 3 sentences and at most 55 words
Statement: keep each beat to 1 to 3 sentences and at most 55 words, one visual step per
  beat.
Why: the census.md files put the median beat at 24.0 (mini-llm) to 33.3 (backpropagation)
  words, and the median of the eight, 26.5, falls between gradient-descent and mlp; 55 is
  twice that rounded up to five, and by a section-rate estimate about one beat in
  twenty-five passes it, mostly a single long sentence (analyses neural-networks s22, s25;
  mlp s05; gpt s14).
Apply: every beat's narration has 1 to 3 sentences, counted as the non-blank pieces between
  full stops, exclamation marks and question marks, and at most 55 words as normalize_words
  counts them.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): none.
Scope: every beat; a bridging beat of one or two words is allowed.
Fails: a 70-word beat that explains the whole weighted sum in one breath.
Exemplars: none.

R09 at least one question per 5.5 minutes of script
Statement: speak at least one question per 5.5 minutes of script; further questions may also
  be staged on screen in the learner's words.
Why: the census.md files count 0.000 (gpt) to 0.750 (neural-networks) spoken questions a
  minute; the median, 0.175, between backpropagation and backpropagation-calculus, is one per
  5.7 minutes, rounded down to 5.5; further questions are often staged on screen, as a
  caption or a student's speech bubble (analyses gpt s33; backpropagation s05; mlp s18).
Apply: the beats whose narration contains a question mark number at least max(1,
  ceil(minutes / 5.5)), where minutes is the script's word count as normalize_words counts
  it, divided by 150.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): none.
Scope: the whole script; a question shown only on screen with question_caption still follows
  R03 but does not count here.
Fails: a five-minute script whose narration never asks anything.
Exemplars: viewer-voice.

R10 second person or first person plural, never third person about the learner
Statement: address the viewer as you and the shared work as we; never speak of the learner
  in the third person.
Why: second_person_rate runs 0.015 (mini-llm) to 0.027 (gradient-descent) in the census.md
  files, median 0.0195, between gpt and neural-networks, or about one word in fifty, and the
  narration hands the viewer each task directly (analyses gradient-descent s13; gpt s30;
  backpropagation s05).
Apply: no beat's narration contains the learner, the student, the viewer or the reader,
  singular or plural, in any letter case.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): none.
Scope: narration; a caption written in the learner's own voice may say I.
Fails: a beat saying that the viewer should now see why the bias matters.
Exemplars: viewer-voice.

R11 the first formula follows at least one concrete beat and arrives no later than the corpus first_formula_fraction plus 0.20 of the lesson
Statement: write the first formula only after at least one concrete beat, and no later than
  0.564 of the lesson's words: the corpus first_formula_fraction 0.364 plus 0.20.
Why: first_formula_fraction, the start of the first spoken formula cue as a fraction of the
  video's duration, runs 0.042 (gradient-descent) to 0.628 (gpt) in the census.md files of
  the seven lessons that have a formula, median 0.364 (mlp; mini-llm has none); the kit
  applies the same fraction to the lesson's words, which is equivalent at a steady speaking
  rate. Formulas are assembled from concrete pieces already on screen (analyses
  neural-networks s17; gradient-descent s06; backpropagation s09).
Apply: the first beat whose moves include formula or whose symbol_introduced is not empty
  has a beat with concrete in moves before it, and the beats before it hold at most 0.564 of
  the lesson's words.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the first formula beat's frames show the concrete objects its terms come
  from.
Scope: lessons with a formula or a symbol; a lesson without one passes. The census measure
  times the first spoken formula cue, which trails the formula on screen (every corpus lesson
  with a formula shows one by 0.38 of its length, the latest being gpt s18), so as a deadline
  it is lenient.
Fails: a lesson that opens on the definition of the cost function, or keeps every symbol
  back until its last third.
Exemplars: numbers-before-symbols.

R12 dim, do not delete
Statement: de-emphasize by fading to an opacity of about 0.1 to 0.5 and keep the object on
  screen; remove an object only when the narration retires it.
Why: inactive items drop to half opacity or lower, down to about a tenth, and stay as context
  while one item is lit (analyses backpropagation-calculus s02, s12; gradient-descent s01;
  attention s12; mlp s15; mini-llm s08).
Apply: a beat that narrows attention names in its visual what it keeps and dims the rest
  (focus_and_dim); a later beat restores or reuses the dimmed objects.
Check (storyboard): none.
Check (frames): an object visible at a beat's first frame is still visible, dimmer if
  dimmed, at its last frame unless the narration retires it.
Scope: every de-emphasis; a deliberate clear at a scene boundary (R16) and a stated
  retirement are not deletions. The rule is prescriptive: corpus scenes sometimes fade
  objects out with no word for it (backpropagation s09 b01; gradient-descent s12 b01), and a
  generated lesson dims them instead.
Fails: the other neurons vanish while one neuron is explained and never come back.
Exemplars: dim-not-delete.

R13 captions sit beside their referents
Statement: put every caption, label and brace next to the object it names, joined to it by
  an arrow or a brace when it cannot touch it.
Why: braces hug what they measure (analyses neural-networks s01 b02; attention s27; gpt
  s31), names sit at the tips of the vectors they describe (mlp s13 b02) and a name is
  written just under the term it names (neural-networks s20 b05).
Apply: each caption in a beat's visual names its referent and its place beside it: above,
  below, beside or along an edge.
Check (storyboard): none.
Check (frames): at each mark frame every caption sits next to its referent or is joined to
  it by an arrow or a brace; none waits in a corner away from what it names.
Scope: labels, captions and braces; a running formula or a tally board may keep a fixed
  corner. The rule is prescriptive: corpus scenes often park a claim or a topic label in a
  corner away from what it names (backpropagation s07 b02; gradient-descent s06 b04;
  neural-networks s03 b01), and a generated lesson puts it beside its referent.
Fails: a bias label parked in the top right corner while the bias term sits in the middle of
  the frame.
Exemplars: caption-next-to-referent.

R14 at most 12 primary mobjects on screen
Statement: keep at most 12 primary objects on screen at once; a crowd that reads as one
  object, such as a grid, a montage, a column cut by an ellipsis or a network drawn as one
  diagram, counts as one.
Why: crowds are cut down to a dozen or fewer objects, or shortened with an ellipsis, before
  they are read (analyses gpt s03, s31; attention s33; backpropagation s09).
Apply: each beat's visual lists the primary objects it adds and removes, and no beat has
  more than 12 on screen, counting a grid, a montage, a column cut by an ellipsis or a
  network drawn as one diagram as one.
Check (storyboard): none.
Check (frames): no mark frame shows more than 12 objects the viewer must read separately.
Scope: objects the narration refers to; a montage that shows scale counts as one object.
  The rule is prescriptive: some corpus derivation boards hold well over a dozen separate
  objects (backpropagation-calculus s04 b06, s06 b01; backpropagation s13 b03), and a
  generated lesson spreads such a board over beats instead.
Fails: sixteen labeled thumbnails beside sixteen neurons on top of the full network.
Exemplars: object-budget, montage-scale.

R15 legible at 480p (font size equivalent to at least 24 px at 1080p)
Statement: make every label the narration refers to readable on the 480p draft frames, a
  font size equivalent to at least 24 px at 1080p, and enlarge the one value that matters
  instead of labeling a crowd.
Why: the readout that matters is pulled out and enlarged, while text shown as texture is
  never asked to be read (analyses neural-networks s07, s08; mini-llm s04; backpropagation
  s08).
Apply: a beat that asks the viewer to read a value names it in the visual and enlarges it or
  zooms to it; text meant only as texture is named as texture.
Check (storyboard): none.
Check (frames): every label the narration refers to is readable on the draft contact sheet,
  and no label or object is cut by the frame edge. In a flat or camera scene its run-log box
  stays inside the 14.22 by 8 frame, or inside the logged camera frame in a camera scene; a
  3d scene's boxes are not projected through its camera, so its clipping is judged from the
  mark frames and sheets only.
Scope: text the narration refers to; the cells of a montage and a crowd of decimals shown as
  texture are exempt.
Fails: 784 one-decimal readouts on tiny squares while the narration reads one of them aloud.
Exemplars: zoom-to-one-unit.

R16 scene boundaries are continuous or deliberately cleared
Statement: open a scene on the frame the previous one closed on, on a deliberate clear to
  black or on a declared cut, never on an unannounced jump.
Why: sections open on the board the previous one left, or on a clean black frame (analyses
  backpropagation-calculus s03, s14; backpropagation s13; mini-llm s09), as when a hook's
  last beat clears the frame to black before the next section begins (mlp s01 b04).
Apply: a scene whose opening_state is continue follows a scene whose closing_state is a
  non-blank string; the first scene never opens with continue.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the continuity check compares the last frame before and the first frame
  after every boundary whose opening_state is continue.
Scope: every scene boundary; black and cut are free choices the storyboard states.
Fails: a scene marked continue whose predecessor never says what it leaves on screen.
Exemplars: transitions-reuse-geometry, carry-picture-forward.

R17 transitions reuse geometry
Statement: move from one picture to the next by transforming objects already on screen, a
  copy of a label into a node or edges into a column, rather than cutting to a fresh
  drawing.
Why: networks collapse into chains, edges turn into columns of numbers and words tilt up
  into headers (analyses backpropagation-calculus s02; gradient-descent s14 b03; gpt s22;
  attention s18).
Apply: a beat that changes the picture names in its visual which object on screen becomes
  which new object (provenance, numbers_to_symbol).
Check (storyboard): none.
Check (frames): the transformed objects can be followed from the beat's first frame to its
  last; no fresh drawing replaces them by a cut.
Scope: changes within a scene and across continue boundaries; a deliberate clear (R16)
  starts fresh. The rule is prescriptive: some corpus sections cut to a freshly drawn picture
  or to footage that shares no geometry (backpropagation-calculus s11 b02; gradient-descent
  s16 b02; gpt s08 b03), and a generated lesson transforms instead, or clears at a scene
  boundary under R16.
Fails: a hard cut from the network to a newly drawn column of parameters.
Exemplars: transitions-reuse-geometry, provenance-transform.

R18 one color per role for the whole lesson
Statement: give each role one color for the whole lesson and keep that color for its role;
  two related roles may share a color, as negative weights and cost share RED, and
  everything without a role stays neutral.
Why: sign colors and term colors stay fixed from scene to scene (analyses
  backpropagation-calculus s03; gradient-descent s05; attention s18; gpt s20), and the video
  mergers left out the colors the records disagreed on, attention's value maps and gpt's
  probability bars (video.json of attention and gpt; analyses attention s32, s33; gpt s10,
  s32).
Apply: every colored object in a beat's visual takes its color from a role in lesson.json
  colors or from a neutral white, grey or black.
Check (storyboard): none.
Check (code): check_scenes.py rejects a named color constant in lesson.py that is neither a
  value of lesson.json colors nor neutral, and leaves any other color value, a hex string or
  a ManimColor, to the critics; each frame critic checks its scene's colors against the
  lesson's colors map, which gives each role the same color in every scene, and the
  storyboard and release critics see the whole lesson.
Scope: every scene; WHITE, BLACK and the greys carry no role. The rule is prescriptive:
  corpus lessons often let one color carry unrelated roles (neural-networks GREEN for a lit
  activation in s03 and s04, then for positive weights from s17; mlp PURE_YELLOW for seven
  contract roles; gpt s28 b02 BLUE and RED for singular and plural words), and a generated
  lesson gives each color one role or one pair of related roles.
Fails: green marks a lit activation in one scene and a positive weight in the next.
Exemplars: one-color-per-role.

R19 the contract palette
Statement: use the merged contract palette for the roles a lesson has: positive weights
  BLUE, negative weights RED, bias MAROON_B, cost RED, emphasis PURE_YELLOW; draw
  activations as the brightness of a WHITE fill, and give any further role a color none of
  the lesson's other roles holds.
Why: four of the five video.json contracts that color weights by sign
  (backpropagation-calculus, backpropagation, gradient-descent, gpt) make the positive side
  BLUE, neural-networks alone GREEN, and mlp colors positive values and active neurons BLUE
  as well; all five make negative weights RED, as mlp does negative values; all three with a
  cost role make it RED, all eight lessons give emphasis PURE_YELLOW, and bias splits two to
  two between BLUE and MAROON_B, settled for MAROON_B because BLUE already holds positive
  weights (video.json of all eight lessons; analyses backpropagation-calculus s08;
  backpropagation s09; neural-networks s18).
Apply: in a lesson about networks or their training, lesson.json colors maps weight_pos to
  BLUE, weight_neg to RED, bias to MAROON_B, cost to RED and emphasis to PURE_YELLOW, and
  the storyboard draws activations as WHITE fill brightness; any other lesson maps emphasis
  to PURE_YELLOW and each of its own roles to one color.
Check (storyboard): none.
Check (code): check_scenes.py rejects a named color constant outside lesson.json colors and
  the neutral colors; any other color value, a hex string or a ManimColor, is left to the
  frame critic, as in R18.
Scope: the five mappings hold in lessons about networks and their training. A lesson without
  weights, bias or cost keeps emphasis PURE_YELLOW and may give its own roles any color,
  BLUE, RED and MAROON_B included, as long as each role keeps one color (R18): mini-llm
  gives BLUE to user labels and RED to errors, and attention RED to values, neither contract
  having a weight role (video.json of mini-llm and attention), and gpt and mlp give BLUE or
  RED to user prompts, temperature and rejections beside their weights (video.json of gpt
  and mlp), which R18 does not let a lesson with weights copy. mlp colors positive values
  and active neurons BLUE and negative values and inactive neurons RED (mlp s14 b02, s15
  b05); a generated lesson draws activations as WHITE brightness instead, so that BLUE stays
  with the weights.
Fails: positive weights in GREEN and bias in BLUE, which puts the bias in the color the rest
  of the corpus gives positive weights.
Exemplars: one-color-per-role.

R20 background #000000
Statement: keep the background #000000 in every scene; dimming overlays and reveals that
  hide text in black depend on it.
Why: every lesson plays on black (the background role, BLACK, of the video.json of
  neural-networks, backpropagation-calculus and mini-llm), and reveals hide text by coloring
  it black against it (analyses backpropagation-calculus s11; gradient-descent s22).
Apply: no beat's visual asks for a background color or a full-screen card other than black.
Check (storyboard): none.
Check (code): manim.cfg sets background_color to BLACK and look.apply sets each scene's
  camera background to BLACK. Nothing rejects a background or a full-screen card set later in
  lesson.py (check_scenes.py accepts the neutral greys, GREY_E among them), and no rubric item
  scores R20, so the scene coder keeps the black the kit sets.
Scope: every scene. The dark grey full-screen cards of the 2024 videos (attention s08) are
  not used; a framed panel gets a rectangle instead.
Fails: a title spoken over a full-screen dark grey card.
Exemplars: one-color-per-role.

R21 the pipeline stays on screen while its parts are explained
Statement: while one stage of a pipeline is explained, keep the whole pipeline visible,
  shrunk or dimmed if needed, so the stage is always seen in place.
Why: the network stays pinned at the side while its formulas are built, and the token row
  stays up while each stage is worked (analyses neural-networks s23, s25; attention s24; mlp
  s11).
Apply: the beats that explain a stage keep the pipeline on screen, closing_state says where
  it sits, and the stage being explained is lit (flash_along).
Check (storyboard): none.
Check (frames): every mark frame of an explaining beat shows the pipeline, smaller or dimmer
  if needed. No rubric item scores R21, so the frame critic counts a lapse only where it also
  meets an item's anchor, under that item's rule ids: a pipeline that vanishes with no word for
  it is an unexplained removal under dim not delete (R12).
Scope: lessons built around a pipeline; an aside with a saved layout (R23) may leave it
  briefly. The rule is prescriptive: some corpus sections drop the pipeline for a full-frame
  detail (neural-networks s19; backpropagation s09 b01), and a generated lesson keeps it in
  view.
Fails: a cut to a full-frame graph of the sigmoid with the network gone.
Exemplars: pipeline-stays-on-screen, light-the-path.

R22 the recurring cast keeps its position
Statement: give each recurring object a home position and return it there every time it
  appears.
Why: formulas, readouts and insets keep one corner across many sections (analyses
  backpropagation-calculus s02, s05; backpropagation s10; attention s15).
Apply: closing_state names the position of each recurring object, and a later scene that
  shows it again places it there.
Check (storyboard): none.
Check (frames): a recurring object sits in the same place in every frame it appears in. No
  rubric item scores R22, so the frame critic counts a lapse only where it also meets an item's
  anchor, under that item's rule ids.
Scope: objects shown in two or more scenes; a move the narration announces is allowed. The
  rule is prescriptive: the corpus network often changes place between sections
  (neural-networks s14, s16, s21, s22; gradient-descent s03, s22), and a generated lesson
  gives it one home.
Fails: the network docked left in one scene, at the bottom in the next and centered in the
  third, with no reason given.
Exemplars: recurring-cast.

R23 layout is saved and restored around an aside
Statement: save the layout before an aside or a close-up and restore it exactly afterwards,
  so the viewer returns to the same picture.
Why: the network shrinks to an inset for an aside and grows back, and a camera pose saved
  before a zoom is restored after it (analyses neural-networks s05; gpt s12, s31; mlp s04).
Apply: a beat that starts an aside or a close-up names the group whose layout it saves, and
  the beat that ends it restores that group (save_and_restore_layout).
Check (storyboard): none.
Check (frames): the first frame after the aside matches the last frame before it in the
  saved group's positions and sizes. No rubric item scores R23, so the frame critic counts a
  lapse only where it also meets an item's anchor, under that item's rule ids.
Scope: asides and close-ups inside a scene; a new scene follows R16 instead. The rule is
  prescriptive: some corpus asides end without the saved picture, a lifted neuron leaving a
  gap that never closes (gradient-descent s17 b03) or an earlier state of the scene coming
  back in place of the paused frame (neural-networks s24 b01), and a generated lesson restores
  the layout it saved.
Fails: after a close-up of one neuron the network returns at a different size and place.
Exemplars: save-and-restore.

R24 run_time 1 s for confirmations, 2 s for meaning-carrying transforms, 3 to 5 s for multi-part reveals, 8 to 12 s for orbits; every lands visual is on screen at its mark frame (the sync gate of section 6.12 measures it)
Statement: give a confirmation 1 s, a transform that carries meaning 2 s, a reveal of
  several parts 3 to 5 s and a camera orbit 8 to 12 s, and land every lands visual on screen
  at its mark frame.
Why: recounted from the census.md bins of all eight lessons, which sum the analysis records'
  timing fields, with each distinct play counted once and montage plays left out (the
  corrections are in docs/experiments/2026-m2-framework-tests.md), 87 percent of the run_time
  literals fall in the 1, 2 and 3 to 5 s bands, the 2017 lessons leaning to 1 s and the 2024
  lessons to 2 and 3 to 5 s, and the camera orbits played as one move mostly run 8 to 12 s
  (analyses gpt s25, s30; mlp s09; mini-llm s01).
Apply: each beat's visual says which kind each play is, and each lands entry names the
  visual that must be on screen at its mark.
Check (storyboard): none.
Check (code): none in check_scenes.py, which reads no run_time literal; manimce.md gives the
  scene coder the four bands, and the frame critic scores the pacing under the rubric's
  motion item from the six-frame sheet. For the lands clause, verify.py runs its sync gates:
  each beat's run-log entry and exit match the section index (run log vs section index) and
  every mark falls inside its beat (marks inside beat); frames: every lands visual is on
  screen at its mark frame (the rubric's sync item).
Scope: plays in a generated scene. The orbit band holds only in a 3D scene. The 2017 lessons'
  3D shots (the cost surfaces of gradient-descent s11 and s12 and backpropagation s19 b05)
  are clips rendered outside the scene code and carry no run_time, so their 8 to 12 s bins
  are empty or nearly so (gradient-descent's three are a vector sweep and two curve draws,
  not orbits). The bands say how long each kind of play runs, not how many of each a lesson
  needs. Montage flipbooks, counters and slow ambient rotations (R26) fall outside them.
Fails: a 0.5 s snap for the transform that carries the lesson's main idea, or a 25 s play
  for a reveal in three parts.
Exemplars: camera-as-narrator, micro-timing-in-one-play.

R25 wait 1 s after most plays, 2 s closing a step
Statement: wait 1 s after most plays and 2 s at the close of a step.
Why: recounted from the census.md bins of all eight lessons, which sum the analysis records'
  timing fields, with each loop counted once and montage holds of 0.5 s or less left out
  (the corrections are in docs/experiments/2026-m2-framework-tests.md), 74 percent of the
  wait literals are 1 s and 14 percent are 2 s (2017 lessons 15 to 43 percent at 2 s, 2024
  lessons 6 to 11 percent); the 2 s wait closes a step (analyses neural-networks s20;
  backpropagation-calculus s09; gradient-descent s12; gpt s26).
Apply: a beat's visual names the play that closes a step, which a 2 s wait follows, and
  most other plays it lists are followed by a 1 s wait, all inside the beat's narration time.
Check (storyboard): none.
Check (code): none in check_scenes.py, which reads no wait literal; manimce.md gives the
  scene coder the 1 s and 2 s waits, and the frame critic scores the pacing under the
  rubric's motion item from the six-frame sheet.
Scope: waits between plays; the holds of a montage, 0.5 s or less per item, and long holds
  (R26) are outside it.
Fails: 0.2 s pauses between every step of a derivation, so no step settles.
Exemplars: staggered-reveal.

R26 long holds only where narration, ambient motion or an orbit carries the moment
Statement: hold a picture for 3 s or more only while narration runs over it, an updater
  keeps it moving or the camera orbits; never hold a still, silent frame for 3 s or more.
Why: the long holds play under twitching edges, turning axes, settling dots or an orbit,
  with the narration running (analyses neural-networks s21; attention s14; gradient-descent
  s04; mlp s09).
Apply: a beat's tail_s stays under 3 s unless its visual names the updater or orbit that
  keeps the picture moving through the tail; a hold of 3 s or more under narration needs no
  motion.
Check (storyboard): none.
Check (frames): frames across a silent hold of 3 s or more change.
Scope: holds inside narrated beats; an end card is outside the lesson. The corpus edit often
  trims scripted holds (neural-networks s27, s30), so code waits overstate what airs.
Fails: a 10 s silent hold on a finished diagram.
Exemplars: motion-with-a-reason, camera-as-narrator, knobs-tremor.

R27 lag_ratio near 1/n for crowds, 0.1 to 0.5 for sequential reveals
Statement: stagger a crowd of n similar items, which the narration does not name one by one,
  at a lag_ratio near 1/n, so the sweep reads as one wave; stagger a sequential reveal of
  items named in turn at 0.1 to 0.5. From 20 items on, 1/n is 0.05 or less, and the corpus
  crowds run 0.001 to 0.05.
Why: the 2024 lessons sweep pixels, streaks, grid cells and letters at 0.001 to 0.05 or 1/n
  and reveal lists item by item at 0.1 to 0.5 (analyses gpt s17, s25; attention s16, s18;
  mlp s23, s28).
Apply: a beat whose visual staggers a group says how many items it holds and whether they
  form a crowd, not named one by one and staggered near 1/n, or a sequential reveal, named
  in turn and staggered at 0.1 to 0.5.
Check (storyboard): none.
Check (code): none in check_scenes.py, which reads no lag_ratio literal; manimce.md gives the
  scene coder the crowd and reveal ratios, and the frame critic scores the staggers under the
  rubric's motion item from the six-frame sheet.
Scope: LaggedStart and staggered plays: crowds near 1/n, sequential reveals at 0.1 to 0.5.
  The 2017 literals do not carry over. Before ManimGL's February 2019 rewrite, which
  ManimCE's lagged start follows, a LaggedStart lag_ratio was each item's share of the play,
  so the 2017 values of 0.2 to 0.8 played as overlapping waves, at most a few times 1/n in
  today's terms (backpropagation s07 b02; backpropagation-calculus s10 b01, s13 b04;
  neural-networks s23 b04), and a lagged start over a group's parts ran each part for half
  the play, about 1/n, as for the 784 pixels of neural-networks s16; the 2017 crowd sweeps
  thus agree with the crowd band. The 0.5 now in that s16 code is a later substitution for
  the old lagged start, which in ManimCE gives each of the 784 cells about 5 ms of a 2 s
  play, so the grid blinks on instead of washing in. A crowd of a few dozen fanned out one
  after another at 0.1 (mini-llm s06, 59 boxes, about six times 1/n) is the upper edge the
  corpus shows, and the rule does not adopt it; a counting sweep, in which a counter rises
  as each item lights in turn (count_parameters), is paced by its count and falls outside
  both bands. Reveals past 0.5 also occur (mlp s16 b05 at 0.7; mini-llm s06 b07, the last of
  eight stages spaced at 1.5 in the 30 s play of b03 to b07): past 0.5 each item is mostly
  done before the next starts, and past 1 gaps open between them, so a generated lesson
  plays such steps as separate plays with R25's waits instead of staggering past 0.5.
Fails: a 784-cell grid staggered at 0.5.
Exemplars: staggered-reveal.

R28 at least one beat per lesson admits an uncertainty or names a simplification
Statement: give at least one beat to admitting an uncertainty or naming a simplification,
  and say why it is made.
Why: every lesson concedes what is arbitrary, unknown or left out, often while the
  simplified picture stays on screen (analyses neural-networks s09; attention s14;
  gradient-descent s10; mlp s02).
Apply: at least one beat of the lesson lists aside in moves.
Check (storyboard): storyboard_check.py evaluates the Apply predicate.
Check (frames): the aside beat keeps the simplified picture on screen while it is named.
Scope: every lesson; the aside move marks the beat that carries the admission.
Fails: a lesson that presents the sigmoid as how every network works, with no word that it
  is one choice among several.
Exemplars: admit-uncertainty.

R29 an honest lie is labeled when shown
Statement: when a picture simplifies, label it as a simplification on screen at the moment
  it is shown, not only in speech or scenes later.
Why: simplifications carry a written label beside the picture, a heading, a struck-through
  claim or an approximately-equal sign (analyses gpt s21; attention s02; backpropagation
  s11; mlp s06, s24).
Apply: a beat that shows a simplified or invented picture names its on-screen label in the
  visual.
Check (storyboard): none.
Check (frames): the simplified picture and its label share the beat's mark frame.
Scope: pictures the narration knows to be simplified or made up; a toy announced on screen
  as a toy counts as labeled. The rule is prescriptive: several corpus simplifications are
  flagged only in speech, or labeled scenes later (neural-networks s19 b03, corrected in
  s29; gradient-descent s04 b02; mlp s10 b04), and a generated lesson labels them on screen
  when shown.
Fails: the sigmoid shown as the standard choice with no flag on screen, corrected only
  scenes later.
Exemplars: honest-lie.

R30 real data only where cheap, seeded synthetic data everywhere else
Statement: use real values only where they are cheap to put in the scene, a published count
  or a small table typed in, and draw every random-looking value from a seeded generator so
  a re-render matches.
Why: published model sizes and totals anchor the arithmetic, and seeded generators make
  random examples replay identically (analyses gpt s19; mlp s21; backpropagation-calculus
  s02, s08).
Apply: no beat's visual names an image, a photo, a dataset file or a download; synthetic
  values come from LayeredNetwork called with the lesson seed, or, for the values passed to
  NumericColumn and WeightGrid, from a random.Random seeded with the lesson seed.
Check (storyboard): none.
Check (code): check_scenes.py rejects ImageMobject, open, Path, requests and urllib in
  lesson.py, and the scene coder passes the lesson seed to every noun helper that takes one.
Scope: all data a lesson shows. The rule is prescriptive: several corpus lessons show
  photos, dataset images or filmed footage (gradient-descent s26; gpt s13; mini-llm s10;
  neural-networks s12; mlp s29), and a generated lesson does not, since the skill renders
  originals only and check_scenes.py rejects ImageMobject; it draws a vector stand-in
  instead, such as a digit as a grid of squares whose fill opacities are pixel values typed
  into the storyboard. Corpus scenes either set a seed of their own, in the scene or in a
  parent class (backpropagation-calculus s02; mini-llm s03, s07; attention s35), or leave the
  seeding to ManimGL's Scene (attention s10 b02, s16 b02), whose random_seed is 0 unless a
  scene sets another, so either way their random values replay on every render; ManimCE
  seeds from config.seed, which is unset by default, so a generated lesson passes the lesson
  seed to every random value.
Fails: digits loaded from a dataset file, or edges jittered by an unseeded random call.
Exemplars: real-data-where-cheap, seeded-randomness.
