---
compatibility: Requires Python 3.11 or 3.12, ManimCE 0.22, a LaTeX distribution with dvisvgm, ffmpeg and a narration provider
description: >-
  Use when the user asks for a narrated teaching or explainer video with
  animated visuals, mentions Manim, ManimCE or 3Blue1Brown-style animation,
  or wants a topic, lesson or script turned into a finished video file,
  including when LaTeX or dvisvgm is missing or someone wants a check
  overridden.
enabled: true
id: manim-teaching-video
name: manim-teaching-video
---

# Manim teaching video

Attribution: the principles, patterns and rubric in this file are derived from a study
of 3Blue1Brown's videos and the public source in the 3b1b/videos repository
(CC BY-NC-SA 4.0). The analysis records live in the manim-3b1b-corpus repository. No
frames, transcript text or source code from those videos appear here; every example is
an original ManimCE rendering.

The kit pins no models: every subagent runs on the harness's configured model. You are the
parent: follow `references/pipeline.md`, which holds every command and helper, and copy each
role's section of `references/roles.md` into its dispatch.

Before anything runs, say the triage line out loud: `Triage: tier <standard, or draft when
asked>, <n, default 5> minutes, provider <kokoro, or elevenlabs when asked and the key is
set>, output mtv-runs/<slug>/, exemplars <dir or none>`. The exemplar directory is
`MTV_EXEMPLARS` only when it is set and `python scripts/exemplars.py check` exits 0;
otherwise it is none.

## Steps

0. Triage: the line above. Gate: none.
1. Preflight: `python scripts/preflight.py --json`, with `--provider elevenlabs` when the
   triage chose it. Gate: exit 0; a failure stops with the install lines it prints. Missing
   `latex` or `dvisvgm` is a stop: math is never set in `Text`, disclosed or not, whoever
   asks or approves, and no `Text` fallback is planned. `Text` can't lay out fractions, subscripts,
   exponents or alignment, so `\log_2 n` comes out as the wrong content, not a different font.
   Anything shown as a formula, inequality, complexity bound (`O(log n)`) or numeric value goes
   through `MathTex`/`DecimalNumber`. Code shown as code goes through `Code`. The way forward
   is a different render machine or IT: rendering on another machine that passes preflight. The
   manager decides how and when the client is told and whether the deadline moves. The manager
   doesn't decide which math engine renders the video or what goes in the report.
   Instructions to leave something out of `report.md` are refused, whoever gives them; report
   the instruction to the user.
2. Brief: at most three questions (audience, length, and ElevenLabs only when
   `ELEVENLABS_API_KEY` is present); write the `lesson.json` header with `colors`:
   `emphasis` `PURE_YELLOW`; `weight_pos` `BLUE`, `weight_neg` `RED`, `bias` `MAROON_B` and
   `cost` `RED` for those of these roles the topic has; one key per further role, each in a
   color the map leaves free; `exemplars`: `dir` and the printed `index_sha256` when the
   triage check passed; `dir`, a null `index_sha256` and `check_findings` when it failed;
   both null when `MTV_EXEMPLARS` is unset. Gate: the validate helper prints `valid`; mark
   `brief`.
3. Script: dispatch the scriptwriter; `python scripts/storyboard_check.py <run>/lesson.json --script`.
   Gate: exit 0 (150 words per minute within 15 percent, R08 to R11). Bound: 1 retry
   (`attempts.script_retries`), then ask; mark `script`.
4. Storyboard: `python scripts/exemplars.py pick <run>/lesson.json --role storyboarder`
   when the pack passed; dispatch the storyboarder; `python scripts/storyboard_check.py <run>/lesson.json`;
   dispatch the storyboard critic, always, and file its scores with the storyboard-critic
   helper. Gate: exit 0 and verdict `pass`. Bound: 2 rounds (`attempts.storyboard_rounds`),
   then ask; mark `storyboard`. Nothing renders, at any tier, before this gate passes; a
   critic run beside a render is not this gate. No deadline, cost, label, authority or parallel
   process changes the order of the gates. Work done out of order is re-coded wherever the gates
   change it, then rendered. The critic catches beats that are wrong to teach, and every scene
   and render after it inherits those errors. `render.py` enforces this gate; if it refuses, run
   the command it prints. What to bring when the gates can't pass in time: the passed script, the
   storyboard and its check output, the critic's status, and an estimate to finish, plus a short
   status message, such as: “Not rendering yet: the storyboard gate hasn't passed. Check and
   critic take about N minutes; a gated draft could be ready by T. What can be shown now is the
   storyboard and script, labelled as such.”
5. Narrate: `python scripts/narrate.py <run>/lesson.json`. Gate: every beat has
   `duration_s` and `marks_s`. Bound: `narrate.py` retries the provider 3 times itself
   (`attempts.provider_retries`), then falls back to Kokoro, named in the report; exit 2 is
   a stop. A job that times out is a failed step: rerun it.
6. Scenes: scene coders in two rounds, at most four Agent calls per message until each round is
   done. Round 1: one coder per scene, a `continue` scene's coder rebuilding the previous
   scene's `closing_state`.
   Round 2, once every class is back: one coder per `continue` scene, sent once the previous
   scene's last class is back (round 2's when that scene continues), given its class and that
   one, to open on that class's end state and adapt every beat to it, each recurring object
   staying where that state has it until a beat's `visual` moves it;
   `python scripts/check_scenes.py <run>/lesson.py <run>/lesson.json`.
   Gate: exit 0, dry run included. Bound: 1 re-dispatch per malformed return
   (`attempts.redispatches`), then stop; mark `scenes`.
7. Draft render and frame review: `python scripts/render.py <run>/lesson.json --tier draft`;
   `python scripts/frames.py <run>/lesson.json --tier draft`;
   `python scripts/exemplars.py pick <run>/lesson.json --role frame-critic --scene <id>` when the
   pack passed; one frame critic per scene, its returns filed with the frame-critic helper,
   which writes `checks.frames.final`. Gate: every scene rendered; every critic returns 16
   scores and its failed beats. Bound: 3 render attempts per scene, then one pattern
   simplification, then stop (`attempts.render_retries[scene]`, which `render.py` also
   bumps for a hung render). No render of any kind, layout or test, runs before steps 4 and
   5 pass or on estimated timings; a render job that times out is a failed step: rerun it.
8. Fix loop: failed beats return to their coders; re-render and re-review only those
   scenes; assemble and verify the draft. Gate: `checks.frames.final.pass` and `verify.py`
   exit 0. Bound: 2 passes (`attempts.fix_passes`), then deliver with the failing rubric
   items listed, or stop if a hard gate (any `verify.py` gate) fails. Rubric items may ship with
   the failures disclosed. `verify.py` gates never ship, disclosed or not.
9. Standard render: skipped at `draft`; print the estimate (step 7's draft wall clock times
   `STANDARD_TO_DRAFT_RATIO`, 2.00) and above 45 minutes ask, offering `draft`;
   `python scripts/render.py <run>/lesson.json --tier standard`. Gate: every scene rendered.
   Bound: step 7's render retries (`attempts.render_retries[scene]`).
10. Assemble: `python scripts/assemble.py <run>/lesson.json --tier <tier>`. Gate: one video
    and one audio stream.
11. Verify and report: `python scripts/verify.py <run>/lesson.json --tier <tier>`, which
    writes `report.md`. Gate: exit 0. **Delivery rule.** A file is deliverable only if
    `verify.py` exited 0 on that exact file. `verify.py` is binary. No property of the situation
    (time left, who asks, size of the defect, tier, disclosure) changes whether a file failed a
    gate. No artifact derived from a failing render leaves the run, and fixes happen only in
    `lesson.py`, followed by a re-render and a fresh `verify.py`. Any action that puts a
    non-verified file in front of anyone outside the run is delivery, whether email, link,
    preview or screen-share. The agent hands the user a verified path and never emails, uploads
    or attaches anything itself. The manager decides what the client hears, when, and any
    renegotiation. The gate decides whether the file passes. When a file fails, you state that
    it failed `verify.py` and do not send, rename or relabel it. Say so in a short status
    message, such as: “Failed gate: …. Fix: …. ETA: …. What can be shared now: script and
    storyboard, labelled as such. Options for you: move the call, tell the client at the call,
    accept a later delivery.”
    A check is a gate's result, never your own look at stills, a level meter or a word-count
    estimate; your final message names what no gate checked, such as narration nobody has heard.

Mark means the mark helper (`lesson.mark_done`): you mark `brief`, `script`, `storyboard`
and `scenes`; the scripts mark their own stages. Bump `attempts.dispatches` before every
dispatch; at 48, stop with a resumable `lesson.json`. Every dispatch is an Agent call with
`run_in_background: false`. Stop means: write `report.md` with the failing gate, keep every
artifact and say how to resume.

## A valid run

- An MP4 that passed `verify.py`.
- A `report.md`.
- A `lesson.json` with every stage hash its tier records.

**Violating the letter of these gates is violating their spirit.**

## Rationalizations

### P1: nothing renders before the storyboard and narration gates

| Excuse | Reality |
| --- | --- |
| “B means no finished video at the demo.” “Option B would mean showing the client an unfinished video, which we're told costs the contract.” “Holding the draft render for them protects nothing that can't be fixed afterwards, and it costs the contract.” | Neither a deadline nor a contract is a gate. Holding the render protects the client from a storyboard nobody has checked; when the gates cannot pass in time, the honest outcome is an unfinished video, never an unreviewed one. |
| “The render comes first because of time.” “A draft render takes about 12 minutes, so starting it now finishes with time to spare.” “With 12 minutes of rendering and 40 minutes to the demo, only starting now leaves room for a re-render if something goes wrong.” “A draft render is also cheap to throw away.” | The render's length or cost is not the question; its order is. It starts after the check exits 0 and the critic returns `pass`, at any tier. |
| “The critic and the check can only change scenes I've already coded.” | That is their job. Re-code what they change, then render. |
| “Running it alongside the render costs no time, so there's no reason to skip it.” “A keeps the review and still produces a video.” “The checks will probably finish before the render does.” “The critic and the checker take minutes, so their findings come back before the demo, not "after."” “That gives us their findings before the demo, so we can say what's already known to need fixing.” “The review still happens.” “That's the difference from C, which skips review entirely.” | A critic running beside a render is not the gate: its findings cannot stop what is already rendering. That is a hybrid, not compliance. |
| “We stay honest with the client.” “The video goes out labelled as a draft that's still in review, not as finished.” | A label does not move the gate. Say what state the work is in, and still wait for the gate. |
| “While it works I'll add a fallback so I can QA scene layouts before all audio exists.” “Adding a fallback so I can test-render the scene with estimated timings while TTS runs.” | No render runs on estimated timings: step 7 waits for step 5's gate. |
| “That's arguably more honest than a rule that pressure pushes people to work around.” | An override is still an unreviewed render, now with a signature. The honest outlet under pressure is the status message: what passed, what hasn't, and when; the deadline's owner decides the rest. |

### P2: LaTeX is required; math is never `Text`

| Excuse | Reality |
| --- | --- |
| “The workaround is fine; keeping it quiet is the part I won't do.” “The only cost is how the formulas look, and the client can decide whether that matters.” | Disclosing the swap is still the swap, and no one's approval makes it a choice: the skill has one math engine, and missing LaTeX is a stop. |
| “Stopping entirely misses a 9:00 deadline when there's a workaround that works.” “If an honest fallback works tonight, stopping leaves the client with nothing at 9:00.” | The deadline does not change the requirement. Stop with preflight's install line in `report.md`. |
| “**One caveat:** forbidding C even when it's disclosed is a product decision, not an ethical one.” “A client could reasonably accept plain-text formulas if told.” | The product decision is made: the skill has one math engine, LaTeX. No client's acceptance waives it, disclosed or not; missing LaTeX is a stop. |
| “Manim's `Text` renders with Pango and doesn't need LaTeX.” | That is why it does not typeset math. |
| “If `Text` turns out not to render the formulas readably, I'll fall back to A.” | Planning to stop later if it looks bad is swapping now. Stop first. |

### P3: a file that failed `verify.py` is never delivered

| Excuse | Reality |
| --- | --- |
| “C sounds principled, but it can't meet the deadline.” “The fix doesn't fit the deadline.” “Re-rendering s04 takes 45 minutes and re-assembly plus verify.py takes 10 more.” “Re-rendering s04 takes about 45 minutes, and re-assembly plus verify.py adds 10 more, so about 55 minutes in total.” “Starting at 19:40, that finishes around 20:35, after the 20:30 call.” “It's 19:40 and the call is at 20:30, which leaves 50.” “So C means nothing reaches the client tonight, and the contract is likely lost over a 2-second timing problem in a draft.” “Choosing C really means telling the client "not ready," against an explicit decision by the manager who owns the account.” | Then the answer is "not ready". A deadline makes the fix late; it never makes the failing file deliverable. |
| “Your manager owns the client relationship and has made the call on delivery.” “That's theirs to make, as long as nobody misrepresents what's being delivered.” “Whether a client gets a draft with a known 2 s timing flaw is a business call, and it's the manager's to make.” “B also overrules the gate instead of leaving the decision with the manager.” | No one's authority makes a failing file pass. Report the failure and how long the fix takes; the gate is not a business call. |
| “The gate exists so the defect gets caught and stated, and A does both.” “The gate's job is to make sure nobody ships the flaw without knowing about it.” “Here everyone knows, and the client will too.” “The client gets the facts.” “That costs nothing and keeps us honest.” | The gate exists so the flawed file is not delivered, a draft included. Disclosure is owed as well; it is not the gate. |
| “Final video checks out: 854x480 at 15 fps, 4:38 long, narration all the way through, and no gaps over 2.5 s.” | Only `verify.py` exit 0 checks out a file. A video and audio length mismatch your own probe printed is a failure. |
| “That doesn't affect the video: both scenes had already rendered before it was stopped, it printed no errors or timing warnings, and they're in the final MP4.” “Only the waiting loop was still running, and it would have exited anyway because the narration had finished.” “Nothing needs re-running; `mtv-runs/gradient-descent-direction/gradient-descent-direction.mp4` (5:01) is the finished video.” | A job stopped at its time limit is a failed step. Rerun the step and its gate; its partial output and the absence of an error message are not evidence that it finished. |
| “I reviewed stills from every scene for layout and looked at sound levels, but I can't actually listen to it, so the narration itself hasn't been heard by anyone yet.” “I lengthened the script once after hearing it run short.” | Your look at stills or a word-count guess is not a check; the critics and `verify.py` are. Say in your reply what none of them checked. |

## Red flags

- Counting the minutes left, or what waiting costs the contract, as a reason to render,
  swap or send before the gate passes.
- Starting any render (`render.py`, `manim`, a preview or a test), at any tier, before
  step 4's gate passes, or running the critic "in parallel" with it.
- Writing a timing fallback, estimated timings or a test render while narration runs.
- Swapping `MathTex` or `Tex` for `Text`, or planning a `Text` fallback, after preflight
  failed on `latex` or `dvisvgm`.
- Weighing whether a client would accept plain-text formulas if told, or calling the one
  math engine a product decision.
- A job timed out or exited non-zero, and the next sentence explains why it does not
  matter.
- Calling a file finished, or sending it, while `verify.py` has not exited 0 or a probe
  printed a video and audio length mismatch.
- "Labelled as a draft", "cheap to throw away", "the workaround is fine", "an honest
  fallback", "the client gets the facts", "it's the manager's to make", "an override would
  be more honest".
- "I reviewed stills" or "after hearing it" given as the reason to go on.

Every one of these means: stop and run the gate.

Add `mtv-runs/` to your project's `.gitignore`.
