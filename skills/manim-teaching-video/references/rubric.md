# Rubric: sixteen items for a narrated lesson

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

Sixteen items, each scored 0, 1 or 2 against the anchors below, for a total out of 32. The
storyboard critic scores a storyboard with them, each frame critic one rendered scene and the
release critic a finished video. The item names are the keys every critic returns, spelled
exactly as the Item column spells them. The Rules column names the rules of framework.md that
an item scores, and a critic that files a lapse under an item cites those rule ids. The notes
after the table say what each anchor means in a storyboard and on the frames, so a critic needs
no other file to score.

## Items

| Item | 0 | 1 | 2 | Rules |
| --- | --- | --- | --- | --- |
| hook before definition | opens with a definition or formula | opens with context but no working thing | opens with a working thing or a concrete puzzle | R01 |
| destination previewed | no preview | preview stated in words only | preview shown, then hidden until earned | R02 |
| value before symbol | a symbol appears before any value | values and symbols arrive together | every symbol transforms from a shown value | R07 |
| one idea per scene | a scene carries two or more ideas | a scene drifts once | each scene has one idea named in its title | R04 |
| question before answer | no question planted | a question is stated but answered at once | a question is planted and held across at least one beat | R03 |
| honesty beat | no admitted uncertainty or simplification | mentioned in passing | a beat names what is simplified and why | R28, R29 |
| picture carried into recap | recap is text only | recap reuses one object | recap rebuilds the lesson's picture from its own objects | R06 |
| voice | beats over 55 words or third person about the learner | one voice rule broken once | all four voice predicates hold | R08 to R11 |
| role colors | colors change meaning | one inconsistency | one color per role for the whole lesson | R18, R19 |
| dim not delete | objects vanish without reason | one unexplained removal | every de-emphasis is a fade to low opacity | R12 |
| captions beside referents | captions in a fixed corner | one caption far from its referent | every caption adjacent to what it names | R13 |
| object budget | more than 12 primary mobjects | one crowded beat | at most 12 primary mobjects per beat | R14 |
| legible at 480p | text unreadable on the draft frames | one small label | every label readable on the draft contact sheet | R15 |
| boundaries continuous | a jump cut with opening_state continue | one boundary rebuilt roughly | every boundary continuous, cleared or an approved cut | R16 |
| motion with a reason | motion that teaches nothing, or teleporting objects | one unmotivated move | every move carries meaning, staggers and eased travel where the corpus uses them; scored from the six-frame sheet | R17, R24 to R27 |
| sync | the named visual is absent at a mark frame | within one beat but late or early beyond the lead | the named visual is on screen at every mark frame | R24 |

## Pass

A lesson passes at 25 of 32 or more with no item at 0. The bar is the same at every stage:

- The storyboard critic's verdict is pass when its scores meet the bar and no visual names an
  image, a photo or a real dataset (R30). It scores sync and motion with a reason 1, so its
  total is at most 30.
- Each frame critic scores one scene. The final score of an item is its minimum across the
  scenes, which the parent files as checks.frames.final in lesson.json, and the bar applies to
  that vector.
- The release critic scores the whole video from its frames and lesson.json.

Calibration: paraphrased storyboards of one 2017 and one 2024 section of the corpus must score
at least 27 of 32 with the storyboard critic. Each section is scored as a part under step 4 of
How to score: unless it is its lesson's first or last section it holds neither the lesson's
first beat nor its last scene, so hook before definition and picture carried into recap score
2 and destination previewed scores the end of the preview and payoff it holds. A lower score
rewrites the rubric item that lost the points, never the corpus.

## How to score

1. Score each item 0, 1 or 2, a whole number, by its anchors as its note below reads them. The
   score is the lowest anchor the scored material meets anywhere, however good the rest is.
2. Nine items name a single lapse in their 1 anchor: one idea per scene, voice, role colors,
   dim not delete, captions beside referents, object budget, legible at 480p, boundaries
   continuous and motion with a reason. For these one lapse scores 1 and a second lapse scores
   0, so their 0 anchors read as the lapse repeated, except where the note names a worse
   failure that scores 0 at once: a scene with two ideas, a color that changes meaning, a jump
   cut at a continue boundary. The other seven items grade how serious a lapse is, so their
   worst lapse decides, however often it occurs.
3. Score what you were given. An item the material cannot show scores 1, never 0 or 2: a
   critic given no frames at all, the storyboard critic or a critic reading a script or code
   alone, scores sync and motion with a reason 1. Such a 1 marks no lapse, so step 5 files
   nothing for it.
4. Score the part you were given. Whether the material is the whole lesson or a part of it is
   set by what the critic is dispatched to score, never read off its lesson.json: a frame
   critic scores one scene, and a calibration scores one section of a corpus lesson as a part,
   even though its lesson.json numbers the section's scenes from s01, gives it a title of its
   own and may open it on black; the storyboard critic and the release critic of a generated
   lesson score the whole lesson. An item whose subject the part does not hold scores 2, as
   each note says: hook before definition outside the lesson's first beat, picture carried into
   recap outside its last scene, sync in a scene with no lands entry. A part that holds one end
   of the lesson's preview and payoff scores the end it holds, as the note on destination
   previewed says. A symbol the part introduces is judged against the shows_value_of of every
   earlier beat of the lesson, which a frame critic is given, as storyboard_check.py's R07
   reads them, so a value an earlier scene showed counts as shown, as the note on value before
   symbol says. The final score takes each item's minimum across scenes, so a scene with no
   place for an item must not lower it. Whether a generated lesson as a whole has a hook, a
   preview, a question, an admission and a recap is scored by the critics that see all of it,
   the storyboard critic and the release critic, and storyboard_check.py fails a storyboard
   without a hook, a question, an admission or a recap before anything renders (R01, R06, R09,
   R28).
5. For every item scored 0 or 1, except a 1 that step 3 gives, say where each lapse is (a beat
   id, or a file and line for a critic reading code), give the rule ids from the item's Rules
   column that it breaks, and give one sentence of reason. The storyboard critic sends a lapse
   that only new words can fix to the scriptwriter as a wording request instead. The request
   rewords beats the lesson already has, never adds, drops or splits one, and opens with the
   item and its rule ids, as in "honesty beat, R28: say in this beat that the sigmoid is one
   choice among several, and why we use it", so it is that lapse's citation.
6. Evidence. In a storyboard the lesson.json fields carry it: the scene's title, opening_state
   and closing_state, and each beat's narration, visual, moves, introduces, shows_value_of,
   symbol_introduced, lands and marks, and the lesson's colors. A run without lesson.json is
   scored from its script, its storyboard text and its scene code. On frames it is each beat's
   six-frame sheet (six tiles evenly spaced over the beat, each stamped with its time), its mark
   frames (one still at each mark, taken when the narration reaches the marked word), its last
   frame and each scene's first frame.

## Notes on the items

### hook before definition

Scores the lesson's first beat (R01). 2: the first beat shows something that visibly works, a
machine running on an input or a process in motion, or poses a puzzle the viewer can try,
before any term is defined; in lesson.json its moves list hook. 1: the lesson opens on
context, a title, a plan, a pointer to another lesson or a motivation, and the working thing
arrives later, still before any definition or formula. 0: a definition, a formula or the
meaning of a term comes before anything works on screen. On frames, the first beat's sheet
shows the working thing in motion and no definition or formula. A part without the lesson's
first beat scores 2.

### destination previewed

Scores the preview and the payoff of the lesson's destination, the finished picture or result
it builds toward (R02). 2: an early beat shows the destination, a following beat takes it away,
and it returns only when built from objects that the beats in between drew. 1: the preview is
stated in words only, or the destination is shown but never hidden, staying on screen
throughout, or it comes back whole instead of being built. 0: no preview: the destination
first appears at the payoff with nothing announcing it. A lesson of separate facts, with no one
picture to build toward, has nothing to preview and scores 2. A part holding neither the
preview nor the payoff scores 2. A part holding only the preview scores it: 2 when the
destination is shown and then taken away, 1 when it stays on screen to the part's end or is
stated in words only. A part holding only the payoff scores it: 2 when the destination is
built from objects that the beats before it drew, 1 when it comes back whole. Such a part
takes the preview as given, since it lies before the part, unless the part begins with the
lesson's first beat, where a payoff with no preview before it scores 0. Whether the lesson
previews its destination at all is scored by the critics that see the whole lesson, the
storyboard critic and the release critic. On frames, a preview is the destination on one
beat's sheet or mark frame and gone from a later beat's, and a payoff that is built shows its
parts moving into place across the sheet's tiles.

### value before symbol

Scores every beat that introduces a symbol, a letter or a formula that stands for a quantity,
such as w, b, a, sigma of a weighted sum or C (R07). In lesson.json the symbols are the entries
of symbol_introduced and the values the entries of shows_value_of. A value counts as shown
before a symbol when a strictly earlier beat of the lesson lists its quantity in shows_value_of,
in the part scored or in an earlier scene, the test storyboard_check.py applies; a frame critic
is given the shows_value_of and symbol_introduced of every beat before its scene for this and
takes those earlier values as shown, since it has no frames of them, while within its own scene
it judges from the frames. 2: every symbol arrives after a beat that shows its quantity as a
number, by transforming a copy of that number or of the object that holds it (numbers_to_symbol,
provenance), and the number stays on screen as the symbol lands; a value an earlier scene showed
is on screen when the scene carried it in across a continue boundary or drew it again before the
symbol. A recap may show a symbol already earned, and a symbol an earlier beat introduced stays
earned. 1: values and symbols arrive together: a symbol arrives in the same beat as the first
value of its quantity, or after it but written fresh instead of transformed from it, as when a
scene writes a symbol whose value only an earlier scene showed and that value is no longer on
screen. 0: a symbol appears before any beat of the lesson has shown a value of its quantity. A
part that introduces no symbol scores 2.

### one idea per scene

Scores every scene (R04). 2: each scene carries one idea, named in its title, and everything
the scene introduces serves that idea; a recap scene may revisit the ideas it names together,
and the opening scene's idea is its working thing. 1: a scene drifts once: a beat or two take up
a second idea and the scene comes back, or a title names something other than what its scene
does. 0: a scene carries two or more ideas, each introduced and worked, or a second drift
anywhere. In a storyboard, compare each scene's title with the introduces of its beats; on
frames, any title on screen matches its scene's title.

### question before answer

Scores every question the lesson plants and the beats up to its answer (R03). A question is
planted when a beat asks it, aloud with a question mark or on screen in the learner's words
(question_caption), rhetorical questions included, and held when its answer comes in a later
beat. 2: questions are planted and held across at least one beat, and no question is answered
in the beat that asks it. 1: a question is stated but answered at once, its answer or a new
object or symbol arriving in the beat that asks it, or a question is left as the lesson's last
beat. 0: no question is planted anywhere in the lesson. On frames, the asking beat's last frame
shows what the question is about and no answer yet. A part with no question scores 2.

### honesty beat

Scores the beats that admit an uncertainty or a simplification and every picture the narration
knows to be simplified or made up (R28, R29). 2: at least one beat names what is simplified,
unknown or chosen arbitrarily and says why, with the simplified picture still on screen; in
lesson.json its moves list aside. Every simplified picture carries a label on screen when it is
shown: a heading, a struck-through claim, an approximately-equal sign, or a toy announced on
screen as a toy. 1: mentioned in passing, as a clause inside another point with no reason
given, or a simplified picture shown with no label on screen. 0: no admitted uncertainty or
simplification anywhere in the lesson. A part with no admission and no simplified picture
scores 2.

### picture carried into recap

Scores the lesson's last scene (R06). 2: the recap brings back the lesson's own picture, objects
first drawn earlier, rebuilt or replayed, and restates the idea on it; the recap introduces
nothing new, and in lesson.json its recap beats have empty introduces and symbol_introduced. 1:
the recap reuses one object beside a text list or a formula, or it carries the picture and then
introduces something new. 0: the recap is text only, a list of statements with none of the
lesson's pictures, or the lesson has no recap. A part without the last scene scores 2.

### voice

Scores the narration of every beat (R08 to R11), counted as storyboard_check.py counts it. A
break is any of these:

- a beat with more than 55 words, or with no sentence or more than three, sentences being the
  non-blank pieces between full stops, exclamation marks and question marks; a bridging beat of
  one or two words is fine (R08);
- fewer beats with a question mark in their narration than max(1, ceil(minutes / 5.5)), where
  minutes is the script's word count divided by 150 (R09);
- a beat whose narration speaks of the learner, the student, the viewer or the reader, singular
  or plural, in place of you and we (R10);
- a first formula, the first beat that writes a formula or introduces a symbol (in lesson.json a
  formula move or a symbol_introduced entry), that comes before any concrete beat, one that works
  an example with actual values (a concrete move), or after 0.564 of the lesson's words (R11).

Each beat that breaks R08 or R10 is one break; R09 and R11 count once each for the lesson. 2: no
break, so all four voice predicates hold. 1: one break. 0: two or more. The question count and
the place of the first formula are scored only on a whole script; a critic holding a part, one
scene or one section, scores R08 and R10 there.

### role colors

Scores every colored object against one role map for the whole lesson (R18, R19). In a lesson
about networks or their training the map is the contract palette: positive weights BLUE,
negative weights RED, bias MAROON_B, cost RED and emphasis PURE_YELLOW; activations are the
brightness of a WHITE fill; any further role takes a color none of the lesson's other roles
holds, such as GREEN or TEAL; and WHITE, BLACK and the greys carry no role. Negative weights and
cost share RED as a related pair, and no other color may carry two roles. A lesson without
weights, bias or cost keeps emphasis PURE_YELLOW and may give its own roles any color, BLUE, RED
and MAROON_B included, one color per role. 2: every role keeps one color for the whole lesson
and the palette above holds. 1: one inconsistency: one object drawn in a color its role does not
hold, or one network role given a color other than the palette's though kept throughout. 0:
colors change meaning: one color stands for two unrelated roles anywhere in the lesson, or a
second inconsistency. In a storyboard, read the colors map and the colors each visual names; on
frames, compare the sheets of every scene the critic is given.

### dim not delete

Scores every de-emphasis and every removal (R12). 2: every de-emphasis fades the object to an
opacity of about 0.1 to 0.5 and keeps it on screen (focus_and_dim), and an object leaves only
when the narration retires it or a scene boundary clears the frame on purpose. 1: one
unexplained removal: one object that vanishes, fades out or is replaced while the narration
still treats it as context. 0: objects vanish without reason: a second unexplained removal. On
frames, an object on a beat's first frame or first tile is still on its last frame, dimmer if
dimmed, unless the narration retires it. In a storyboard, a visual that narrows attention names
what it keeps and dims the rest.

### captions beside referents

Scores every caption, label and brace (R13). 2: each sits next to what it names, above, below,
beside or along an edge, or is joined to it by an arrow or a brace; a running formula or a tally
board may keep a fixed corner. 1: one caption far from its referent with no arrow or brace to
it. 0: captions in a fixed corner: a second caption away from what it names. On frames, check
the mark frames; in a storyboard, the place each visual gives its captions.

### object budget

Scores the primary objects on screen at once: the objects the narration refers to or the
viewer must read separately (R14). A grid, a montage, a column cut by an ellipsis or a network
drawn as one diagram counts as one object. 2: no beat has more than 12 primary objects on
screen at any frame. 1: one crowded beat, with more than 12. 0: more than 12 primary objects in
a second beat. On frames, count on the mark frames and sheets, helped by the bounding-box log;
in a storyboard, count the objects each visual adds and removes.

### legible at 480p

Scores every label the narration refers to or asks the viewer to read (R15). A label needs a
font size equivalent to at least 24 px at 1080p: about 11 px on an 854 by 480 draft mark frame
and about 5 px on a contact sheet tile, which is half that size. A label that cannot be read on
its tile is checked on the mark frame before it counts as a lapse. Text shown as texture, the
cells of a montage or a crowd of decimals no one reads aloud, is exempt. A label or an object
cut by the frame edge is a lapse of this item too. In a flat or camera scene the run log shows
it: the object's box, taken at the beat's end, lies partly outside the 14.22 by 8 frame or, in
a camera scene, outside the camera frame logged for that beat. A 3d scene's boxes are not
projected through its turned or zoomed camera, so its clipping is judged from the mark frames
and sheets only. 2: every such label is readable and nothing is cut by the frame edge, and
the one value the narration reads is enlarged or zoomed to. 1: one small label, or one label or
object cut by the frame edge. 0: text unreadable on the draft frames: a second label too small
to read or a second one cut. In a storyboard, a visual that asks the viewer to read one value
out of a crowd without enlarging it is the lapse.

### boundaries continuous

Scores every scene boundary: the last frame of one scene against the first frame of the next,
and the opening_state the storyboard gives the second scene, which is continue, black or cut
(R16). 2: every boundary is continuous, the continue scene opening on the frame that its
predecessor closed on and that its predecessor's closing_state describes, cleared to black, or
an approved cut, one the storyboard declares with opening_state cut. 1: one boundary rebuilt
roughly: a continue scene opens close to the previous closing frame but with objects moved,
resized or redrawn. 0: a jump cut with opening_state continue, a jump at a boundary the
storyboard does not declare, or a second rough boundary. In a storyboard, a continue scene
whose predecessor's closing_state is blank or names a different picture is the lapse. A part
holding no boundary scores 2.

### motion with a reason

Scores every play, wait and hold from the six-frame sheets, read with their time stamps (R17,
R24 to R27). An unmotivated move is any of these:

- a cut to a freshly drawn picture where an object already on screen could have been
  transformed into it (R17);
- an object that jumps to a new place or size with no travel or transform between (a teleport);
- a play far outside its band, such as a half-second snap for the transform that carries the
  lesson's main idea or a 25 s play for a reveal in three parts; the bands are a run_time of 1 s
  for a confirmation, 2 s for a transform that carries meaning, 3 to 5 s for a reveal of several
  parts and 8 to 12 s for a camera orbit in a 3D scene (R24);
- plays chained with no pause to settle, where most plays want a wait of about 1 s after them
  and the play that closes a step about 2 s (R25);
- a still, silent hold of 3 s or more that no narration, updater or orbit carries (R26);
- a crowd of similar items the narration does not name one by one that blinks on at once or
  ticks on one by one instead of washing in as one wave at a lag_ratio near 1/n (0.05 or less
  from 20 items on), or a sequential reveal of items named in turn staggered outside 0.1 to 0.5
  (R27).

Montage flipbooks, counting sweeps (count_parameters) and slow ambient rotations under narration
fall outside the timing bands. 2: every move carries meaning: objects travel or transform from
what was on screen, eased rather than jumping, a crowd washes in as one wave and a list is
revealed item by item. 1: one unmotivated move. 0: motion that teaches nothing, or teleporting
objects: a second unmotivated move. A critic reading a storyboard, a script or code alone scores
this item 1.

### sync

Scores every lands entry: the visual it names against the mark frame taken when the narration
reaches its mark (R24). The kit lands each visual 0.2 s before its mark, the lead, which is too
short to see on frames, so a visual is on time when it is on screen and complete at its mark
frame and not already complete at the beat's previous cue, the mark frame of the previous mark
or, for a first mark, the frame the beat opens on (the previous beat's last frame, or the
scene's first frame for its first beat). 2: every named visual is on screen at its mark frame
and lands on its cue. 1: within one beat but late or early beyond the lead: a visual still
arriving or missing at its mark frame that completes later in the same beat, on a later tile
or the last frame, or one already complete at the beat's previous cue. 0: the named visual is
absent at a mark frame and does not arrive within its beat. A critic given no frames at all,
the storyboard critic or a critic reading a script or code alone, scores this item 1. A scene
with no lands entry holds nothing for this item and scores 2.
verify.py's sync gates (run log against the section index, every mark inside its beat) are hard
gates outside the score; this item scores what the frames show.

## Rules no item scores

R05 (zoom to one unit before the crowd), R20 (background #000000), R21 (the pipeline stays on
screen), R22 (the recurring cast keeps its position), R23 (layout saved and restored around an
aside) and R30 (real data only where cheap) have no item. The storyboarder and the scene coder
apply them from their references. The kit's manim.cfg and look.apply set the black background
of R20, check_scenes.py rejects the names R30 bans, and the storyboard critic fails a
storyboard whose visual names an image, a photo or a real dataset with a failed beat whose item
is null and whose rule id is R30. A lapse of one of the others that also meets an item's
anchor, such as a pipeline that vanishes with no word for it, is scored under that item with
that item's rule ids.
