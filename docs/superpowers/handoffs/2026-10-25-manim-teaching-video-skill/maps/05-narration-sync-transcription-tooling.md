# Narration, sync, transcription and keyframe tooling

Design map 05 for the 3Blue1Brown-grade narrated ManimCE video skill. Researched on 2026-10-25 from
primary sources only: shallow GitHub clones, raw GitHub files, PyPI JSON metadata, and the GitHub web UI
through WebFetch. Every claim cites a local file path with line numbers, a PyPI record, or a fetched page;
anything else is marked **unverified**.

## Research conditions and confidence legend

Reachable from this container: `github.com`, `raw.githubusercontent.com`, `pypi.org`. WebFetch resolved
only `github.com`; DNS failed for `platform.openai.com`, `developers.openai.com`, `openai.com`,
`elevenlabs.io`, `huggingface.co`, `ffmpeg.org`, `scenedetect.com` and `learn.microsoft.com`, so vendor
pricing pages and model cards could not be read. WebSearch worked and is used only for secondary,
clearly labelled hints.

Local evidence directories:

- `/home/user/ManimCommunity/manim-voiceover` (clone, HEAD `3dc0d95`, 2026-06-15)
- `/home/user/yt-dlp/yt-dlp` (clone, HEAD `fa98866`, 2026-10-23)
- `/home/user/slhck/ffmpeg-normalize` (clone)
- `/tmp/claude-0/-home-user--agents/b713d8f3-7c52-540b-8252-65c41f426313/scratchpad/raw/` and
  `.../scratchpad/readmes/` (raw files fetched from GitHub, named by project)
- `/tmp/claude-0/-home-user--agents/b713d8f3-7c52-540b-8252-65c41f426313/scratchpad/pypi/` (PyPI JSON)

Confidence levels used below:

- **High**: read the source code or official docs text directly.
- **Medium**: primary source for the mechanism, secondary source for a number (price, speed).
- **Low**: secondary sources only, or inference; treat as a hypothesis to verify in implementation.

Container facts (checked): ffmpeg 6.1.1 built with `--enable-libass --enable-libfreetype
--enable-libfontconfig --enable-libx264 --enable-libaom --enable-libmp3lame --enable-libopus`; filters
`select`, `showinfo`, `scdet`, `thumbnail`, `subtitles`, `ass`, `loudnorm`, `ebur128`, `concat`, `amix`,
`adelay`, `apad`, `silencedetect` are present; 4 CPUs, 15 GB RAM, Python 3.13.17, Node 22 at
`/opt/node22/bin/node`, Bun at `/root/.bun/bin/bun`; no `deno`, `espeak-ng`, `sox`, `manim`, LaTeX.

## 1. manim-voiceover

Repository: <https://github.com/ManimCommunity/manim-voiceover>. PyPI: <https://pypi.org/project/manim-voiceover/>.

### Identity, release cadence and license

| Fact | Value | Evidence |
| --- | --- | --- |
| Latest PyPI release | 0.4.0, uploaded 2026-06-14 | `scratchpad/pypi/manim-voiceover.json` |
| Previous release | 0.3.7, 2024-09-29 (20-month gap) | same PyPI record, release list |
| Latest commit | `3dc0d95` 2026-06-15 "Update demo link in README" | clone `git log -1` |
| Recent authors | 10 most recent commits (Jun 13-15 2026) all by `osolmaz` | WebFetch of `/commits/main` |
| License | MIT | `LICENSE:1`, `pyproject.toml:7` |
| Python | `>=3.11` | `pyproject.toml:6` |
| Stars / open issues | 321 / 45 | WebFetch of the repo page (2026-10-25) |
| Development status | "3 - Alpha" classifier | `pyproject.toml:21` |
| Quality gates | ruff, ty, strict mypy, pytest coverage `fail_under = 85`, mutmut, pip-audit | `AGENTS.md`, `pyproject.toml:153` |

Runtime dependencies (`pyproject.toml:36-45`): `manim` (unpinned), `sox`, `python-dotenv`, `mutagen`,
`pydub`, `pip`, `pydantic>=2.10`, `python-slugify`. Extras (`pyproject.toml:47-73`): `azure`, `gtts`,
`openai` (`openai>=1.6.1,<2`), `pyttsx3`, `recorder` (PyAudio, pynput), `translate` (deepl),
`elevenlabs` (`elevenlabs>=0.2.27,<0.3`), `gemini` (`google-genai`), `transcribe`
(`openai-whisper>=20230314`, `stable-ts>=2.6.2,<3`).

System packages the docs require: SoX >= 14.4.2 for speed changes (`docs/source/installation.rst:71-91`),
PortAudio only for the recorder (`installation.rst:41-69`), gettext only for translation
(`installation.rst:93-110`). Manim must be run with `--disable_caching`
(`installation.rst:17-19`).

### VoiceoverScene API

Source: `src/manim_voiceover/voiceover_scene.py`.

- `set_speech_service(speech_service, create_subcaption=True)` stores the service and resets the
  tracker; subcaptions are disabled when `config.save_last_frame` is set (lines 24-43).
- `voiceover(text=None, ssml=None, **kwargs)` is a `@contextmanager` that yields a `VoiceoverTracker`
  and, in `finally`, calls `wait_for_voiceover()` so the scene never runs ahead of the audio
  (lines 181-217). SSML raises `NotImplementedError` (lines 143-144). Extra kwargs `subcaption`,
  `max_subcaption_len` (default 70) and `subcaption_buff` (default 0.1 s) are popped; the rest go to the
  speech service (lines 200-203).
- `_add_voiceover_text()` calls `speech_service._wrap_generate_from_text`, builds the tracker, restores
  `self.renderer.skip_animations = self.renderer._original_skipping_status`, then `self.add_sound(...)`
  with the cached audio file and adds wrapped subcaptions (lines 74-105).
- `wait_for_voiceover()` waits for `tracker.get_remaining_duration()`; `safe_wait(duration)` only waits
  when `duration > 1 / config["frame_rate"]` (lines 153-169).
- `wait_until_bookmark(mark)` waits `tracker.time_until_bookmark(mark)` (lines 171-179).

Example usage pattern (original, not copied from the repo):

```python
from manim import Circle, Create
from manim_voiceover import VoiceoverScene


class Demo(VoiceoverScene):
    def construct(self):
        self.set_speech_service(my_service)
        with self.voiceover(text="Watch the <bookmark mark='c'/>circle appear.") as tracker:
            self.wait_until_bookmark("c")
            self.play(Create(Circle()), run_time=tracker.get_remaining_duration())
```

### Tracker, duration and bookmarks

Source: `src/manim_voiceover/tracker.py`.

- `VoiceoverTracker.__init__` reads `duration` from the final audio file, sets `start_t` from
  `scene.renderer.time` and `end_t = start_t + duration`; bookmarks are processed only when the cache
  entry has `word_boundaries` (lines 35-54).
- Bookmarks are the XML-ish tag `<bookmark mark='x'/>`; the regex is
  `<bookmark\s*mark\s*=['"]\w*["']\s*/>` (`helper.py:115-116`, `tracker.py:103-107`). Each bookmark's
  character offset in the tag-stripped text is mapped to audio time by `TimeInterpolator`, a
  `scipy.interpolate.interp1d` over `(text_offset, audio_offset / 10_000_000)` pairs
  (lines 11-29). Offsets are in 100-nanosecond ticks (`AUDIO_OFFSET_RESOLUTION`, line 11), the Azure
  convention.
- When word boundaries are missing or fewer than two, a linear text-to-time fallback is used with a
  warning (lines 56-76, 82-87).
- `get_remaining_duration(buff=0.0)` returns `max(end_t - renderer.time + buff, 0)` (lines 114-125);
  `time_until_bookmark(mark, limit=...)` is used by the official example
  (`examples/bookmark-example.py:28`).
- Bookmark time error source: the text offset is rescaled by `transcribed_text_len / net_text_len`
  (lines 90-112), and `timestamps_to_word_boundaries` advances `text_offset` by `len(word)` with no
  spaces (`services/base.py:99-120`). Timing is therefore proportional interpolation between whisper
  word starts, not exact phoneme timing. The bookmark example even syncs syllables of
  "Supercalifragilisticexpialidocious" by linear interpolation (`examples/bookmark-example.py:88-116`).

### How word timing is obtained

Source: `src/manim_voiceover/services/base.py`.

1. A service's `generate_from_text()` may return `word_boundaries` itself. Only `AzureService` does,
   through the SDK `synthesis_word_boundary` event (`services/azure.py:230-248`).
2. Otherwise, if a `transcription_model` is set, `_wrap_generate_from_text` transcribes the generated
   audio with `stable_whisper.load_model(model)` and converts segments to word boundaries
   (`base.py:188-195`, `219-245`). The import is `stable_whisper`, so the `transcribe` extra
   (openai-whisper plus stable-ts, both PyTorch) is required (`base.py:231-240`).
3. Defaults for `transcription_model`: `"base"` for ElevenLabs (`services/elevenlabs.py:108`), OpenAI
   (`services/openai.py:49`) and Recorder (`services/recorder/__init__.py:31`); `None` for Gemini
   (`services/gemini.py:169`); not set for gTTS and pyttsx3.
4. `global_speed != 1` re-times audio with SoX (`adjust_speed`) and divides every `audio_offset` by the
   speed (`base.py:200-212`).

### Supported speech services

Source: `docs/source/services.rst:15-61` and `src/manim_voiceover/services/*.py`.

| Service class | Backend | Offline | Native word timing | Notes |
| --- | --- | --- | --- | --- |
| `RecorderService` | Microphone via PyAudio | n/a | no (whisper) | records during render |
| `GeminiService` | Google Gemini TTS, `google-genai` | no | no | "Recommended for AI voices" in README; PCM to WAV (`gemini.py:149-155`) |
| `AzureService` | Azure Speech SDK | no | yes | docs cite 500 min/month free tier |
| `ElevenLabsService` | `elevenlabs` SDK 0.2 API (`generate`, `save`, `voices`) | no | no (whisper) | default model `eleven_monolingual_v1` (`elevenlabs.py:105`) |
| `OpenAIService` | `openai.audio.speech` | no | no (whisper) | default `tts-1-hd`, voice `alloy`, speed 0.25-4.0 (`openai.py:47-83`) |
| `GTTSService` | Google Translate TTS | no | no | undocumented API, may stop working |
| `PyTTSX3Service` | espeak via pyttsx3 | yes | no | rated "Bad" in docs |

Docs line 61 states a free, local, high-quality engine is still on the roadmap; an open issue
"Support for Kokoro TTS" (Nov 25 2025) exists (WebFetch of the issues page).

### Caching behaviour

- Cache directory defaults to `<media_dir>/voiceovers` (`defaults.py:1`, `base.py:148-151`); entries
  are appended to `cache.json` (`defaults.py:2`, `base.py:216`).
- Audio file names are `slug(text, 50 chars)-<first 8 hex of sha256(json(input_data))>`
  (`base.py:247-259`); `input_data` includes service name and config (voice, model, speed), so changing
  a voice invalidates the cache.
- Entries are validated by Pydantic models with `extra="allow"` (`services/cache.py:16-46`).
- Manim's own caching must be disabled (`--disable_caching`) because of a Manim bug
  (`installation.rst:17-19`).

### ManimCE compatibility

- `manim` is unpinned in `pyproject.toml:37`; `uv.lock:1608-1641` resolves to `manim 0.20.1`
  (2026-02-27). PyPI `manim` is 0.22.0 (2026-10-08) and GitHub `main` declares version 0.22.0
  (`scratchpad/raw/manim-pyproject.toml:3`).
- The plugin depends on renderer internals: `scene.renderer.time` (`tracker.py:47`) and
  `renderer._original_skipping_status` (`voiceover_scene.py:87`). Both still exist on Manim `main`
  (`scratchpad/raw/manim-cairo-renderer.py:55-59`, `manim-scene.py:218,288`). Manim `main` also
  introduces a `Manager` (`manim-scene.py:208,322`), so a renderer refactor is a live risk.
- Not exercised against 0.22.0 in CI as far as the lock file shows (uv.lock pins 0.20.1).

### Maintenance risk assessment

Verdict: **moderate-to-high** for direct dependency, **low** for borrowing the design.

- Single active maintainer; a 20-month release gap followed by a burst of commits in June 2026
  (PyPI record; WebFetch of commits).
- Stale service pins: `elevenlabs<0.3` versus current SDK 2.74.1 (2026-10-20), and `openai<2` versus
  3.37.0 (2026-10-22) (`pyproject.toml:50,54`; PyPI records). The ElevenLabs code imports the removed
  0.2-era API (`services/elevenlabs.py:17`), and an open issue titled "Support latest Eleven Labs
  version" exists (WebFetch of issues).
- Word timing requires PyTorch plus openai-whisper plus stable-ts; an open issue (Jun 2 2026) reports
  the whisper install failing with "No module named 'pkg_resources'".
- The useful core is small: `voiceover_scene.py` (238 lines), `tracker.py` and parts of `base.py`.
  Its MIT license allows re-implementing an equivalent, so the skill can treat manim-voiceover as an
  optional adapter and own a minimal `NarratedScene` with the same bookmark semantics but fed by
  timestamp data from the TTS or from forced alignment (see section 3).

Confidence: **High** (code read directly); star/issue counts **Medium** (web UI snapshot).

## 2. Text-to-speech options

Summary table (details and evidence follow).

| Engine | Quality (reported) | Cost | Offline | Word or char timestamps | License | Heavy deps | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kokoro-82M (`kokoro`) | natural, small model | free | yes | yes, per token (English) | Apache-2.0 | torch, transformers, spaCy, espeak-ng | High (code), Medium (speed) |
| Kokoro via `kokoro-onnx` | same model | free | yes | not verified | MIT wrapper, Apache-2.0 model | onnxruntime, espeakng-loader | Medium |
| Piper (`piper-tts`) | clear, less natural | free | yes | phoneme alignments only | GPL-3.0-or-later | onnxruntime (espeak-ng bundled) | High |
| edge-tts | neural (Azure voices) | free, unofficial | no | yes, word boundaries | LGPL-3.0 | aiohttp (unverified) | High (code), Low (ToS) |
| OpenAI TTS | high | per character or token | no | no | API | `openai` SDK | High (API shape), Low (price) |
| ElevenLabs | highest reported | subscription credits | no | yes, per character | API | `elevenlabs` SDK | High (API shape), Low (price) |
| Azure Speech | high | pay-as-you-go, free tier | no | yes, word boundaries | API | Azure SDK | Medium |
| gTTS | medium | free, unofficial | no | no | MIT | none | High |
| pyttsx3 / espeak-ng | low | free | yes | no | MPL-2.0 | espeak-ng | High |

### Kokoro

Sources: `scratchpad/readmes/kokoro.md`, `scratchpad/readmes/kokoro-pyproject.toml`,
`scratchpad/raw/kokoro-pipeline.py`, `scratchpad/raw/kokoro-model.py`,
`scratchpad/raw/misaki-pyproject.toml`, `scratchpad/pypi/kokoro.json`. Repository:
<https://github.com/hexgrad/kokoro>. PyPI: <https://pypi.org/project/kokoro/>.

- Model: 82 M parameters, "Apache-licensed weights" (README paragraph 2). Package license Apache-2.0
  (`kokoro-license.txt:1-3`, `kokoro-pyproject.toml` classifier). GitHub shows 9.7k stars and 176
  issues; the five most recent commits are dated Jun 30 to Aug 6, 2025 (WebFetch). PyPI 0.9.4 was
  uploaded 2025-04-05, so the project is quiet but not abandoned.
- Install: `pip install kokoro soundfile` plus `apt-get install espeak-ng` for English out-of-dictionary
  fallback and for non-English languages (README "Usage" and "Advanced Usage"). Dependencies:
  `huggingface_hub`, `loguru`, `misaki[en]>=0.9.4`, `numpy`, `torch`, `transformers`
  (`kokoro-pyproject.toml:20-27`). `misaki[en]` pulls `num2words`, `spacy`,
  `spacy-curated-transformers`, `phonemizer-fork`, `espeakng-loader`, `torch`, `transformers`
  (`misaki-pyproject.toml:27`). `espeakng-loader` ships espeak-ng libraries for pip, so the apt package
  is a fallback, not a hard requirement (**Medium**, inferred from the dependency name).
- Python constraint: PyPI 0.9.4 declares `requires_python = <3.13,>=3.10`
  (`scratchpad/pypi/kokoro.json`), while GitHub `main` declares `<3.14` and has a commit
  "Enable Python 3.13 (#244)" dated Aug 6, 2025 (WebFetch). On this container's Python 3.13 the PyPI
  wheel will be refused; install from GitHub or use `kokoro-onnx`.
- Model download host: `hf_hub_download(repo_id='hexgrad/Kokoro-82M', ...)` fetches `config.json`,
  `kokoro-v1_0.pth` and `voices/<voice>.pt` (`kokoro-model.py:27,46,67`, `kokoro-pipeline.py:152`).
  Allow-list `huggingface.co` (and its CDN, unverified host name).
- Voices and languages: `lang_code` `a` American English, `b` British English, `e`, `f`, `h`, `i`, `j`,
  `p`, `z` (README comments); example voice `af_heart`; output 24 kHz float arrays per chunk
  (README `sf.write(..., 24000)`); phoneme chunks are capped at 510 (`kokoro-pipeline.py:274-275`).
- Timestamps: `KPipeline.join_timestamps(tokens, pred_dur)` sets `token.start_ts` and `token.end_ts`
  (seconds) from the duration predictor for every English `MToken` (`kokoro-pipeline.py:295-328`,
  called at 394-396). This gives word timing without any ASR pass, which is exactly what bookmarks
  need.
- CPU feasibility: no official real-time factor exists (README says only "significantly faster"). A
  web search surfaced a community benchmark of RTF about 0.57 (ONNX) and 0.79 (PyTorch) on a 4-core
  Xeon without GPU; **Low** confidence, not fetched. For a 10-minute narration that would be roughly
  6-8 minutes of synthesis on this container's 4 CPUs; measure in implementation.
- `kokoro-onnx` 0.6.1 (2026-08-19, MIT; model Apache-2.0): deps `onnxruntime>=1.20.1`,
  `espeakng-loader`, `phonemizer`, `numpy`; Python `>=3.10,<3.14`; models `kokoro-v1.0.onnx` and
  `voices-v1.0.bin` are downloaded from GitHub Releases (about 300 MB, 80 MB quantized)
  (`scratchpad/readmes/kokoro-onnx.md`, `scratchpad/raw/kokoro-onnx-pyproject.toml`). Whether it
  exposes token timestamps is **unverified**.

### Piper

Sources: `scratchpad/readmes/piper1-gpl.md`, `scratchpad/raw/piper-API_PYTHON.md`,
`piper-VOICES.md`, `piper-CLI.md`, `piper-setup.py`, `piper-download.py`, `piper-voice.py`.
Repository: <https://github.com/OHF-Voice/piper1-gpl>. PyPI: <https://pypi.org/project/piper-tts/>.

- Latest: `piper-tts` 1.8.0 uploaded 2026-09-04; releases v1.8.0 (Sep 4), v1.7.0 (Aug 15), v1.6.1
  (Aug 13) (WebFetch). The old `rhasspy/piper` README says development moved to `OHF-Voice/piper1-gpl`.
- License: `GPL-3.0-or-later` (`piper-setup.py:59`). The GPL applies to the Python package; invoking
  it as a subprocess or library from the skill is fine for use, but bundling its code into the skill
  would make the bundle GPL. Voices carry their own `MODEL_CARD` licenses and Piper is "intended for
  personal use and text to speech research only" (`piper-VOICES.md`, last paragraph).
- Install: `pip install piper-tts`; `install_requires = onnxruntime>=1,<2` (`piper-setup.py:77`);
  espeak-ng data is bundled (`piper-setup.py:9-10`), so no system espeak-ng is needed.
- Voices: `python3 -m piper.download_voices en_US-lessac-medium` downloads from
  `https://huggingface.co/rhasspy/piper-voices/resolve/main/...` (`piper-download.py:13-15`), two files
  per voice (`.onnx` plus `.onnx.json`).
- API: `PiperVoice.load(path).synthesize_wav(text, wav_file, syn_config=SynthesisConfig(...))`;
  `length_scale` controls speed; streaming `synthesize()` yields `AudioChunk`
  (`piper-API_PYTHON.md`). With `include_alignments=True`, `AudioChunk.phoneme_alignments` and
  `phoneme_id_samples` give per-phoneme sample counts (`piper-voice.py:62-69,129-139`), which can be
  aggregated into word timing but is not provided as such.
- Maintenance: README section "Looking for Maintainers" (Open Home Foundation).
- Quality: VITS voices; generally judged less natural than Kokoro in community comparisons
  (**Low**, not measured here).

### edge-tts

Sources: `scratchpad/readmes/edge-tts.md`, `scratchpad/raw/edge-tts-LICENSE`, `edge-tts-setup.cfg`,
`edge-tts-constants.py`, `edge-tts-communicate.py`, `edge-tts-submaker.py`. Repository:
<https://github.com/rany2/edge-tts>. PyPI: <https://pypi.org/project/edge-tts/>.

- Latest 7.3.1 (2026-10-13); releases 7.3.1 and 7.3.0 on Oct 13, 7.2.8 on Mar 22 (WebFetch).
- License: LGPLv3, except `srt_composer.py` which is MIT (`edge-tts-LICENSE:1-2`;
  `edge-tts-setup.cfg` classifier).
- Mechanism: a WebSocket to `speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1`
  with a hard-coded `TrustedClientToken`, a spoofed Edge/Chromium 143 user agent, and a generated
  `Sec-MS-GEC` DRM header (`edge-tts-constants.py:3-16`, `edge-tts-communicate.py:467-468`). Output is
  `audio-24khz-48kbitrate-mono-mp3` (`constants.py`, bottom comment). Custom SSML was removed because
  "Microsoft prevents the use of any SSML that could not be generated by Microsoft Edge itself"
  (README "Custom SSML").
- Timestamps: request `boundary="WordBoundary"` (`communicate.py:335`); the service returns
  `audio.metadata` events with `Offset` and `Duration` in 100-ns ticks (`communicate.py:389-403`,
  `constants.py` `TICKS_PER_SECOND`); `SubMaker.feed()` turns them into SRT cues
  (`edge-tts-submaker.py`). Default voice `en-US-EmmaMultilingualNeural` (`constants.py:9`).
- Terms-of-use risk: the README carries no disclaimer. A web search surfaced a Microsoft Q&A thread in
  which a Microsoft moderator wrote that commercial use of these repositories without an Azure
  subscription "could be a violation of our terms of service"; that page could not be fetched
  (**Low**). The reverse-engineered token and DRM header mean the endpoint can break or be blocked
  at any time. Not suitable as a bundled default; acceptable only as an explicit user opt-in.

### OpenAI text-to-speech

Sources: `scratchpad/raw/openai-speech-params.py`, `openai-speech-model.py` (SDK 3.37.0 types,
generated from the OpenAPI spec). Repository: <https://github.com/openai/openai-python>. PyPI:
<https://pypi.org/project/openai/> (3.37.0, 2026-10-22, Apache-2.0).

- Models: `tts-1`, `tts-1-hd`, `gpt-4o-mini-tts`, `gpt-4o-mini-tts-2025-12-15`
  (`openai-speech-model.py:7`).
- Voices: `alloy`, `ash`, `ballad`, `coral`, `echo`, `fable`, `onyx`, `nova`, `sage`, `shimmer`,
  `verse`, `marin`, `cedar`, or a custom voice id (`openai-speech-params.py:24-33`).
- Limits and knobs: `input` max 4096 characters; `response_format` `mp3|opus|aac|flac|wav|pcm`; `speed`
  0.25-4.0; `instructions` steers delivery but "Does not work with `tts-1` or `tts-1-hd`";
  `stream_format` `sse|audio` (`openai-speech-params.py:14-57`).
- Timestamps: the speech endpoint has no timestamp parameter or field in the SDK types, so word timing
  must come from a later alignment pass (**High** for the SDK shape; the docs page was unreachable).
- Pricing: official page unreachable. Web search aggregators quote `tts-1` at USD 15 per 1M
  characters and `tts-1-hd` at USD 30 per 1M characters, and describe `gpt-4o-mini-tts` as
  token-priced at roughly USD 0.015 per minute of audio; the figures conflict between sources
  (**Low**, unverified). A 10-minute script is about 1,500 words or 9,000 characters, so even `tts-1-hd`
  costs well under one dollar per video at those rates.

### ElevenLabs

Sources: `scratchpad/raw/elevenlabs-tts-client.py`, `elevenlabs-alignment.py`,
`elevenlabs-audio-ts.py` (SDK 2.74.1). Repository: <https://github.com/elevenlabs/elevenlabs-python>.
PyPI: <https://pypi.org/project/elevenlabs/> (2.74.1, 2026-10-20, MIT).

- Timestamp endpoint: `TextToSpeechClient.convert_with_timestamps(voice_id, text=..., model_id=...,
  output_format=..., voice_settings=..., language_code=..., seed=..., previous_text=..., next_text=...,
  previous_request_ids=..., apply_text_normalization=...)` returns `AudioWithTimestampsResponse`
  (`elevenlabs-tts-client.py:185-275`). A streaming variant `stream_with_timestamps` exists
  (line 458).
- Response shape: `audio_base64`, `alignment` and `normalized_alignment`, each a
  `CharacterAlignmentResponseModel` with `characters`, `character_start_times_seconds` and
  `character_end_times_seconds` (`elevenlabs-audio-ts.py`, `elevenlabs-alignment.py`). Character
  timing is finer than any whisper output and is already aligned to the normalized text, which solves
  the number-expansion problem that forced aligners struggle with.
- Continuity: `previous_text`, `next_text` and `previous_request_ids` improve prosody across
  sentence-level requests (docstring, lines 252-260), useful when synthesizing one script section at a
  time.
- Output tiers: MP3 192 kbps needs Creator tier or above; PCM/WAV 44.1 kHz needs Pro or above
  (docstring, `output_format`).
- Pricing: official page unreachable. Web search aggregators list Starter at about USD 5 per month
  for 30,000 credits, Creator USD 22 for 100,000 credits, Pro USD 99 for 500,000 credits, with
  conflicting overage rates (**Low**, unverified). manim-voiceover docs mention a free tier of 10,000
  characters per month (`docs/source/services.rst:204-205`, may be outdated).

### Other services considered

- Azure Speech: the only service with native word boundaries inside manim-voiceover
  (`services/azure.py:230-248`); needs an Azure account with a card even for the free 500 min/month
  (`services.rst:39`). Good premium alternative when ElevenLabs is not wanted. **Medium**.
- Google Gemini TTS: manim-voiceover's recommended cloud voice; no timestamps in the response the
  plugin uses (`services/gemini.py:181-227`). **Medium**.
- gTTS 2.5.4 (MIT): wraps the undocumented Google Translate endpoint; its README disclaimer warns
  breaking changes "can occur without notice" (`scratchpad/raw/gtts-README.md:38-40`). Not for a
  default. **High**.
- pyttsx3 2.99 (MPL-2.0): offline espeak-ng wrapper, `engine.save_to_file`
  (`scratchpad/raw/pyttsx3-README.md:36-39,93`); quality rated "Bad" by manim-voiceover docs. Useful
  only as a smoke-test voice. **High**.
- Coqui TTS: `coqui-tts` 0.28.0 (2026-10-19, MPL-2.0, Python `>=3.10,<3.15`) is the maintained idiap
  fork of the archived `TTS` package (PyPI records). Large models and PyTorch; not examined further.
  **Low**.

### Recommended default and premium voices

- Default for a CPU-only container: **Kokoro-82M**. Apache-2.0 weights, fully offline, 24 kHz, built-in
  per-token timestamps, and a model small enough for 4 CPUs. Stated assumption for the skill: narration
  provider defaults to Kokoro voice `af_heart` (American English) at speed 1.0, installed from GitHub on
  Python 3.13 or from PyPI on Python 3.10-3.12, with `kokoro-onnx` as the lighter fallback when PyTorch
  is unwanted. Piper is the second fallback (GPL, phoneme alignments only).
- Premium option: **ElevenLabs** through `convert_with_timestamps` (character timing, best reported
  naturalness), with **OpenAI `gpt-4o-mini-tts`** as the cheaper premium that needs a forced-alignment
  pass. Azure is the premium choice if native word boundaries and a Microsoft account are preferred.
- Not recommended as defaults: edge-tts (terms-of-use and breakage risk), gTTS (undocumented API).

## 3. Forced alignment for narration-to-animation sync

### whisperX

Sources: `scratchpad/readmes/whisperx.md`, `scratchpad/readmes/whisperx-pyproject.toml`,
`scratchpad/raw/whisperx-alignment.py`. Repository: <https://github.com/m-bain/whisperX>. PyPI:
<https://pypi.org/project/whisperx/> (3.8.6, 2026-05-25, BSD-2-Clause).

- Pipeline: batched faster-whisper ASR, then phoneme-level CTC forced alignment with wav2vec2, optional
  pyannote diarization (README "What is it"). Releases v3.8.6 (May 25), v3.8.5 (Apr 1), 3.8.7rc1
  (Jun 26) (WebFetch).
- Inputs and outputs: `whisperx.align(segments, model_a, metadata, audio, device,
  return_char_alignments=False)` takes transcript segments and returns word `start`/`end`, optionally
  per character (`whisperx-alignment.py:152-159,267,429`). Alignment models default to
  `WAV2VEC2_ASR_BASE_960H` for English via `torchaudio.pipelines`, with Hugging Face fallback
  `facebook/wav2vec2-base-960h` and language-specific HF models (`alignment.py:52-77,124-137`).
- CPU: `whisperx audio.wav --compute_type int8 --device cpu` (README "Usage"). Numba (`whisperx[fast]`)
  accelerates the alignment DP loops.
- Dependencies are heavy: `torch~=2.8.0`, `torchvision`, `torchcodec`, `pyannote-audio>=4.0.0`,
  `transformers`, `ctranslate2`, `faster-whisper`, `triton` on x86 Linux
  (`scratchpad/readmes/whisperx-pyproject.toml:11-25`); `torchaudio` is an optional extra.
- Known limitation: words without dictionary characters such as "2014." or "£13.60" get no timing
  (README "Limitations"). Narration scripts for math videos contain many numerals and symbols, so the
  script must be normalized (numbers spelled out) before alignment.
- Model hosts: `download.pytorch.org` (torchaudio pipelines), `huggingface.co` (HF models, Systran
  whisper weights, pyannote).

### stable-ts

Sources: `scratchpad/readmes/stable-ts.md`, `scratchpad/raw/stable-ts-align.py`. Repository:
<https://github.com/jianfch/stable-ts>. PyPI: <https://pypi.org/project/stable-ts/> (2.19.1,
2025-08-16, MIT).

- Purpose: modifies Whisper to give stable word timestamps (cross-attention DTW plus silence/VAD
  adjustments and regrouping) and adds `align()` for text-to-audio alignment (README "Alignment",
  lines 875-890).
- API: `result = model.align('audio.mp3', text, language='en')`; CLI
  `stable-ts audio.mp3 --align text.txt --language en`. Parameters include `original_split`,
  `max_word_dur` (3.0 s default), `word_dur_factor`, `nonspeech_skip`, `fast_mode` and
  `failure_threshold` which aborts when too many words get zero duration
  (`stable-ts-align.py:27-60`). Output is a `WhisperResult` with word-level timing exportable to SRT,
  VTT, ASS, TSV and JSON (README "Output").
- Backends: default openai-whisper (PyTorch), `stable-ts[fw]` for faster-whisper, `[hf]`, `[mlx]`
  (README lines 385-560). Prerequisites: FFmpeg and PyTorch (README lines 29-60).
- Role today: this is what manim-voiceover calls (`stable_whisper.load_model`). Model weights come from
  `openaipublic.azureedge.net` when using openai-whisper (`scratchpad/raw/whisper-init.py:18-20`).
- CPU cost: one whisper pass of the chosen size over the narration; `base` is a few times faster than
  real time on CPU (openai-whisper README table gives relative speeds only; **Medium**).

### aeneas

Source: `scratchpad/readmes/aeneas.md`. Repository: <https://github.com/readbeyond/aeneas>. PyPI:
<https://pypi.org/project/aeneas/> (1.7.3.0, 2017-03-16, AGPL-3.0).

- Mechanism: synthesizes the text with espeak, computes MFCCs, aligns with DTW to produce a
  synchronization map at any fragment granularity, "single word, subphrase, phrase, paragraph"
  (README "Supported Features"); robust to mispronunciations and noise.
- Requirements: Python 2.7 or 3.5, FFmpeg, eSpeak, numpy, C extensions (README "System
  Requirements"). Last release 2017; AGPL-3.0 is incompatible with bundling in a permissively licensed
  skill.
- Verdict: historically the standard tool, now unmaintained. Do not use.

### torchaudio CTC forced aligner

Sources: `scratchpad/readmes/torchaudio-forced-align.py` (official tutorial),
`torchaudio-forced-align-mms.py`, `scratchpad/raw/torchaudio-w2v2-impl.py`,
`scratchpad/raw/torchaudio-README.md`. Repository: <https://github.com/pytorch/audio>. PyPI:
<https://pypi.org/project/torchaudio/> (2.11.0, 2026-03-23).

- API: `torchaudio.functional.forced_align(emission, targets, blank=0)` returns per-frame token
  alignments and scores; `torchaudio.functional.merge_tokens` collapses them into `TokenSpan` objects;
  frame indices convert to seconds by `waveform_length / num_frames / sample_rate`
  (tutorial lines 143-152, 205-216, 319-320).
- Models: `torchaudio.pipelines.MMS_FA` (multilingual, 1100+ languages, weights from
  `https://dl.fbaipublicfiles.com/mms/torchaudio/ctc_alignment_mling_uroman/model.pt`,
  `torchaudio-w2v2-impl.py:1656-1657`) with a `<star>` token for missing text (tutorial lines 421-446);
  `WAV2VEC2_ASR_BASE_960H` for English (`impl.py:310`, weights on `download.pytorch.org`).
- Inputs: 16 kHz waveform plus a transcript already normalized to the model's character set (lower
  case letters, romanized with `uroman` for other scripts); the MMS tutorial notes that numbers such as
  "1882" are not romanized and must be spelled out (MMS tutorial lines 177-230).
- Status: TorchAudio "transitioned into a maintenance phase"; features deprecated in 2.8 were removed
  in 2.9, but `forced_align` is still listed as a core feature (`torchaudio-README.md:18-39`).
- CPU cost: a single wav2vec2-base forward pass plus a Viterbi DP; faster than real time on CPU for
  minutes-long audio (**Medium**, inferred from model size, not measured).

### Comparison of sync strategies

| Strategy | Where timing comes from | Accuracy | Extra cost | Failure modes |
| --- | --- | --- | --- | --- |
| TTS returns timestamps (Kokoro tokens, ElevenLabs characters, Azure or edge-tts word boundaries) | the synthesizer's own duration model | best available; exact by construction | none | only available for those engines; Kokoro timing is English-only |
| Align afterwards (torchaudio forced_align, stable-ts align, whisperX) | acoustic model aligned to the known script | good on clean synthetic speech; errors on numerals, symbols, abbreviations | one model download and a CPU pass per narration | normalization mismatch between script and spoken form |
| manim-voiceover bookmarks | whisper transcription of the audio, interpolated by character offset | approximate; the plugin itself documents linear interpolation | full ASR pass per voiceover line | transcription errors change `transcribed_text_len`; needs PyTorch plus whisper plus stable-ts |

Synthesized speech is clean, single-speaker and read at a steady pace, so alignment is easier than on
lecture recordings; the dominant risk is text normalization (what the TTS said versus what the script
wrote). ElevenLabs returns both `alignment` and `normalized_alignment` precisely for this reason.

### Recommended alignment path for the skill

1. Prefer engines that return timing (Kokoro default, ElevenLabs or Azure premium) and derive bookmark
   times directly from word or character start times; no ASR pass needed.
2. For engines without timing (OpenAI, Piper, gTTS), run forced alignment of the known script, not
   transcription: `torchaudio.functional.forced_align` with `WAV2VEC2_ASR_BASE_960H` for English
   after spelling out numbers and stripping symbols, or `stable-ts` `align()` when a whisper model is
   already installed. Both operate on the exact script text, so bookmark positions map to word indices
   without the character-offset interpolation manim-voiceover uses.
3. Keep manim-voiceover's `<bookmark mark='x'/>` syntax and `voiceover()` context-manager ergonomics,
   but drive them from a precomputed `words[]` timing table stored next to the audio in the cache.
4. Fall back to proportional interpolation (manim-voiceover's fallback) only when alignment fails
   (`failure_threshold` or missing words), and surface a warning in the quality checklist.

## 4. Corpus transcription of 3Blue1Brown videos

### yt-dlp subtitles and auto-captions

Sources: `/home/user/yt-dlp/yt-dlp/README.md`, `yt_dlp/extractor/youtube/_video.py`,
`test/test_subtitles.py`. Repository: <https://github.com/yt-dlp/yt-dlp>. PyPI:
<https://pypi.org/project/yt-dlp/> (2026.10.21, Unlicense).

- Flags (README lines 891-909, 775, 697, 1060): `--write-subs`, `--write-auto-subs`, `--list-subs`,
  `--sub-format FORMAT` (preference list such as `json3/vtt/best`), `--sub-langs en.*`,
  `--skip-download`, `--write-info-json`, `--convert-subs srt|vtt|ass|lrc`.
- YouTube caption formats offered by the extractor: `json3`, `srv1`, `srv2`, `srv3`, `ttml`, `srt`,
  `vtt` (`_video.py:142`); the test fixture confirms every language is served in those formats
  (`test/test_subtitles.py:60-75`). Auto-captions are the tracks with `kind == 'asr'` and are exposed
  under `automatic_captions`, manual tracks under `subtitles` (`_video.py:4252-4255,4292,4350`).
- Word timing in auto-captions: YouTube's `json3` and `srv3` payloads carry per-word segment offsets
  for ASR tracks; yt-dlp passes them through without parsing. The exact field names
  (`events[].segs[].tOffsetMs`) are from memory and **unverified** here. VTT auto-captions carry
  per-word timing only through inline cue timestamps; manual captions have cue-level timing only.
- YouTube now needs `yt-dlp-ejs` plus a JavaScript runtime for full support; `deno` is the only
  runtime enabled by default, and `--js-runtimes node` enables Node, which this container has
  (README lines 203-215, 367-383). Remote components are off by default (`--remote-components`,
  lines 384-397).
- Suggested corpus command (original):

```bash
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" \
  --sub-format "json3/vtt/best" --write-info-json --js-runtimes node \
  -o "corpus/%(id)s.%(ext)s" "https://www.youtube.com/watch?v=<id>"
```

### faster-whisper on CPU

Sources: `scratchpad/readmes/faster-whisper.md`, `scratchpad/raw/fw-utils.py`,
`scratchpad/raw/fw-transcribe.py`. Repository: <https://github.com/SYSTRAN/faster-whisper>. PyPI:
<https://pypi.org/project/faster-whisper/> (1.2.1, 2025-10-31, MIT).

- CTranslate2 re-implementation, "up to 4 times faster than openai/whisper for the same accuracy"
  with int8 quantization on CPU (README intro). No system FFmpeg needed; audio decoded with PyAV
  (README "Requirements").
- Published CPU benchmark, 13 minutes of audio, `small`, 8 threads on an i7-12700K: faster-whisper
  fp32 2m37s / 2257 MB RAM, int8 1m42s / 1477 MB, int8 `batch_size=8` 51s / 3608 MB; whisper.cpp fp32
  2m05s / 1049 MB; openai/whisper fp32 6m58s (README "Small model on CPU"). Scaling to a 25-minute
  lecture on this 4-vCPU container: roughly 5-8 minutes for `small` int8, 15-30 minutes for
  `medium`, and an hour or more for `large-v3` (**Low**, extrapolated; measure in implementation).
- Word timestamps: `model.transcribe(path, word_timestamps=True)` yields `segment.words` with
  `start`, `end`, `word`, using cross-attention DTW with punctuation merging
  (README "Word-level timestamps"; `fw-transcribe.py:285-328`). `vad_filter=True` with Silero VAD
  removes long silences; `initial_prompt` biases vocabulary.
- Model host: `huggingface.co/Systran/faster-whisper-*` plus `distil-whisper/*-ct2` and
  `mobiuslabsgmbh/faster-whisper-large-v3-turbo` for `turbo` (`fw-utils.py:11-31`).

### whisper.cpp

Sources: `scratchpad/readmes/whisper-cpp.md`, `scratchpad/raw/whispercpp-cli-README.md`,
`whispercpp-cli.cpp`, `whispercpp-download.sh`, `scratchpad/readmes/pywhispercpp.md`. Repository:
<https://github.com/ggml-org/whisper.cpp> (MIT). Python bindings:
<https://pypi.org/project/pywhispercpp/> (1.5.1, 2026-08-22, MIT, prebuilt CPU wheels).

- Build with CMake (`cmake -B build && cmake --build build -j`), download ggml models with
  `models/download-ggml-model.sh base.en` from `https://huggingface.co/ggerganov/whisper.cpp`
  (`whispercpp-download.sh:9`). Memory: tiny 75 MiB disk / about 273 MB RAM, base 142 MiB / 388 MB,
  small 466 MiB / 852 MB, medium 1.5 GiB / 2.1 GB, large 2.9 GiB / 3.9 GB (README "Memory usage").
- Word timing: `-ml 1` (`--max-len 1`) with `-sow` (`--split-on-word`) emits one word per segment;
  `-dtw MODEL` computes token-level DTW timestamps; `-oj`/`-ojf` write JSON
  (`whispercpp-cli-README.md:20-21,43-44,57`; `cli.cpp:165,179,204,1068-1074`).
- Fit: lowest RAM footprint and no PyTorch, but the word timing is less refined than
  stable-ts/faster-whisper DTW plus punctuation handling; good fallback when Python wheels fail.

### openai-whisper reference

Source: `scratchpad/raw/whisper-README.md:58-70`, `whisper-init.py:18-20`. PyPI
<https://pypi.org/project/openai-whisper/> (20250625, MIT). Model sizes: tiny 39 M, base 74 M, small
244 M, medium 769 M, large 1550 M with relative speeds about 10x, 7x, 4x, 2x, 1x. Weights are
downloaded from `openaipublic.azureedge.net`. Slowest CPU option; use only because stable-ts needs it.

### Best transcript for a 25-minute lecture

1. Fetch YouTube manual subtitles when they exist (`--write-subs`); human captions give the most
   accurate text, including notation, but only cue-level timing.
2. Run faster-whisper `large-v3-turbo` or `distil-large-v3` in int8 with `word_timestamps=True`,
   `vad_filter=True` and an `initial_prompt` listing domain terms (neuron, gradient, softmax,
   backpropagation) for a word-timed transcript; fall back to `small.en` if time is short.
3. If manual captions exist, align their text to the audio (stable-ts `align()` or torchaudio
   `forced_align`) to combine correct text with word timing; otherwise use the whisper words.
4. Use YouTube `json3` auto-captions only as a timing cross-check, and `info.json` metadata for
   titles and chapter boundaries (chapter field names **unverified**).

## 5. Keyframe extraction

### ffmpeg scene-change selection

Sources: `scratchpad/raw/ffmpeg-filters.texi` (FFmpeg `doc/filters.texi` on `master`), local
`ffmpeg -filters`.

- `select` exposes a `scene` variable, a "value between 0 and 1 to indicate a new scene"; the
  documented example is `select='gt(scene\,0.4)'` and "Comparing scene against a value between 0.3 and
  0.5 is generally a sane choice" (`ffmpeg-filters.texi:32866-32870,32962-32965`).
- `showinfo` prints `n`, `pts`, `pts_time` (seconds) per frame to stderr
  (`ffmpeg-filters.texi:22741-22770`), so timestamps can be parsed from the log.
- `scdet` is an alternative that sets `lavfi.scd.score` and `lavfi.scd.mafd` frame metadata; good
  thresholds are "in the [8.0, 14.0] range" out of 0-100 (`ffmpeg-filters.texi:22324-22360`).
- Original command for timestamped keyframes:

```bash
ffmpeg -hide_banner -i lecture.mp4 \
  -vf "select='gt(scene,0.3)',showinfo" -fps_mode vfr \
  frames/key_%04d.png 2> frames/showinfo.log
grep -o 'pts_time:[0-9.]*' frames/showinfo.log | cut -d: -f2 > frames/times.txt
```

### PySceneDetect

Sources: `scratchpad/readmes/pyscenedetect.md`, `scratchpad/raw/scenedetect-content.py`,
`scenedetect-cli.md`, `scenedetect-pyproject.toml`. Repository:
<https://github.com/Breakthrough/PySceneDetect>. PyPI: <https://pypi.org/project/scenedetect/>
(0.7.2, 2026-10-12, BSD-3-Clause).

- Install `pip install scenedetect` plus an OpenCV variant or PyAV; OpenCV is required at runtime but
  intentionally not declared (`scenedetect-pyproject.toml:43-58`). ffmpeg or mkvmerge only for
  splitting.
- API: `detect("video.mp4", ContentDetector())` returns `(start, end)` timecode pairs; `AdaptiveDetector`
  handles fast camera motion, `ThresholdDetector` handles fades (README "Quick Start (Python API)").
  `ContentDetector(threshold=27.0, min_scene_len=15)` are the defaults (`scenedetect-content.py:104-107`).
- CLI: `scenedetect -i v.mp4 detect-content list-scenes save-images`; the default detector is
  `detect-adaptive`; `save-images` writes `num-images = 3` frames per scene by default; a stats CSV
  (`--stats`) helps calibrate the threshold (`scenedetect-cli.md:34,118-128,130-133,228`).
- Fit: more robust than the raw `scene` score on slow animations (adaptive ratio against neighbours),
  and it produces scene lists directly. Both tools are cheap on CPU.

### Sampling at transcript-segment boundaries

- Given word-timed transcript segments from section 4, extract one frame per segment start or
  midpoint with `ffmpeg -ss <t> -i lecture.mp4 -frames:v 1 -q:v 2 out.jpg` (fast seek before input).
- Expected counts for a 20-25 minute 3Blue1Brown chapter (**Low**, estimates to calibrate): whisper
  produces roughly 250-400 segments, so one frame per segment yields 250-400 frames; `scene > 0.4`
  on continuously animated content typically yields far fewer true cuts (tens to low hundreds) and
  misses gradual transforms; `scene > 0.3` or PySceneDetect adaptive mode lands in between. Uniform
  sampling every 10 s gives 120-150 frames.
- Recommended set: union of scene-cut frames and segment-midpoint frames, deduplicated within one
  second, capped near 300 frames per video, each named with its timestamp so it joins the transcript
  and source-code alignment tables.

## 6. Video assembly

### What ManimCE already does

Sources: `scratchpad/raw/manim-scene.py`, `manim-scene-file-writer.py`, `manim-section.py`,
`manim-render-options.py` (ManimCE `main`, version 0.22.0).

- `Scene.add_sound(sound_file, time_offset=0, gain=None)` overlays audio at the current scene time
  through pydub `AudioSegment` (`manim-scene.py:1768-1810`, `manim-scene-file-writer.py:382-466`);
  on `combine_to_movie` the mix is exported to WAV and muxed with PyAV, converting to AAC for MP4
  (`scene_file_writer.py:857-935`).
- `Scene.add_subcaption(content, duration=1, offset=0)` collects `srt.Subtitle` entries written as a
  `.srt` next to the movie (`manim-scene.py:1726-1766`, `scene_file_writer.py:986-994`).
- `manim --save_sections` saves "section videos in addition to movie file"
  (`manim-render-options.py:260-264`); `Scene.next_section(name, type, skip_animations)` cuts a
  section, and `combine_to_section_videos` writes one MP4 per section plus a JSON index of
  `Section.get_dict()` entries (`scene_file_writer.py:326-346,966-985`; `manim-section.py:36-83`).
- `--format` accepts `auto|none|png|png-sequence|...` (`manim-render-options.py:153-159`).

### Combining section renders with narration

Assembly plan (ffmpeg 6.1.1 verified locally; filter docs from `ffmpeg-filters.texi` and
`ffmpeg-demuxers.texi`):

1. Render each section silently with ManimCE (`--save_sections`), and produce one narration WAV per
   section whose length defines the section's run time (bookmarks already consumed inside the scene).
2. Concatenate section videos with the concat demuxer, which requires identical codecs and time bases
   (`ffmpeg-demuxers.texi:77-96`): `ffmpeg -f concat -safe 0 -i sections.txt -c copy video.mp4`.
3. Build the narration track by placing each section's audio at the section start with `adelay` and
   mixing with `amix`, or simply concatenating WAVs when sections are back to back; pad with `apad`.
4. Mux: `ffmpeg -i video.mp4 -i narration.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`.

Original end-to-end sketch:

```bash
ffmpeg -f concat -safe 0 -i sections.txt -c copy silent.mp4
ffmpeg -i silent.mp4 -i narration_normalized.wav \
  -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

### Loudness normalization

- ffmpeg `loudnorm` (EBU R128): options `I` (default -24 LUFS, range -70 to -5), `LRA` (default 7),
  `TP` (default -2 dBTP), `print_format=json` for the measurement pass, `linear` mode when measured
  values are supplied, `dual_mono` for mono narration
  (`ffmpeg-filters.texi:5866-5916`). Two-pass use: first pass with `print_format=json`, second pass
  passing `measured_I`, `measured_LRA`, `measured_TP`, `measured_thresh`, `offset`.
- `ffmpeg-normalize` 1.43.0 (2026-10-14, MIT; <https://github.com/slhck/ffmpeg-normalize>,
  <https://pypi.org/project/ffmpeg-normalize/>) wraps the two-pass procedure. Defaults:
  `normalization_type = ebu`, `target_level = -23.0`, `loudness_range_target = 7.0`,
  `true_peak = -2.0` (`src/ffmpeg_normalize/_ffmpeg_normalize.py:108-122`); `--preset podcast` applies
  -16 LUFS (README "What's New", version 1.36.0); ffmpeg 7.x recommended, 5.x and above works
  (`docs/getting-started/requirements.md:7`). Its docs explain when `loudnorm` falls back to dynamic
  mode and recommend `--keep-loudness-range-target --auto-lower-loudness-target` to stay linear
  (`docs/usage/normalization-options.md:25-46`).
- Recommendation: normalize the narration track to -16 LUFS integrated, -1.5 dBTP, before muxing;
  mono input flagged `dual_mono`. Online-video platforms commonly target -14 to -16 LUFS (**Low**,
  general knowledge, not fetched).

### Subtitle burn-in option

- Soft subtitles: mux the Manim `.srt` as `-c:s mov_text` into MP4 (ffmpeg CLI; **Medium**).
- Hard burn-in: the `subtitles` filter "Draw[s] subtitles on top of input video using the libass
  library" and needs an FFmpeg build with `--enable-libass` (`ffmpeg-filters.texi:23829-23836`); the
  container's ffmpeg has it. Example: `ffmpeg -i final.mp4 -vf "subtitles=final.srt" burned.mp4`.
  Fonts come from fontconfig (`fontsdir` option).
- Word-level highlighted captions can be produced as ASS from stable-ts (`result.to_ass()`,
  README "Output") or from the TTS word table, then burned with the `ass` filter.

## 7. Hosts to allow-list for the implementation session

| Host | Needed by | Evidence |
| --- | --- | --- |
| `pypi.org`, `files.pythonhosted.org` | all pip installs | standard; reachable now |
| `github.com`, `raw.githubusercontent.com`, GitHub Releases download host (`objects.githubusercontent.com`, **unverified**) | kokoro from source, `kokoro-onnx` model files | kokoro-onnx README release links |
| `huggingface.co` (plus its LFS CDN, host name **unverified**) | Kokoro weights and voices, Piper voices, faster-whisper Systran models, whisper.cpp ggml models, HF wav2vec2 aligners, pyannote | `kokoro-model.py:46,67`; `piper-download.py:13`; `fw-utils.py:11-31`; `whispercpp-download.sh:9`; `whisperx-alignment.py:63-77` |
| `download.pytorch.org` | torch CPU wheels, torchaudio pipeline weights | `whisperx-pyproject.toml` indexes; `torchaudio-w2v2-impl.py:310` |
| `dl.fbaipublicfiles.com` | torchaudio `MMS_FA` | `torchaudio-w2v2-impl.py:1657` |
| `openaipublic.azureedge.net` | openai-whisper weights (stable-ts default backend) | `whisper-init.py:18-20` |
| `api.openai.com`, `api.elevenlabs.io` | premium TTS | SDK defaults (**unverified** host strings) |
| `speech.platform.bing.com` | edge-tts only | `edge-tts-constants.py:3` |
| `translate.google.com` | gTTS only | gTTS README |
| `youtube.com`, `googlevideo.com`, `ytimg.com`, npm or GitHub for `yt-dlp-ejs` components | corpus download | yt-dlp README lines 203-215, 384-397 |

## 8. Decisions this map supports

1. Narration default: Kokoro-82M (Apache-2.0, offline, built-in token timestamps); premium:
   ElevenLabs `convert_with_timestamps`; alternates: OpenAI `gpt-4o-mini-tts`, Azure. edge-tts and
   gTTS are opt-in only.
2. Sync: consume timestamps from the TTS when available; otherwise forced-align the known script with
   torchaudio `forced_align` or stable-ts `align()`; never rely on transcription of synthesized audio
   as the primary timing source.
3. manim-voiceover: reuse the `voiceover()` context-manager and `<bookmark/>` ergonomics, but
   implement a small timing layer the skill owns, because the plugin's service pins are stale, its
   bookmark timing is interpolated, and it adds a PyTorch-plus-whisper dependency for timing that the
   default TTS already provides.
4. Corpus transcripts: YouTube manual subtitles for text plus faster-whisper (`large-v3-turbo` or
   `distil-large-v3`, int8, word timestamps) for timing; align the two when both exist.
5. Keyframes: PySceneDetect adaptive or ffmpeg `scene > 0.3` cuts, unioned with transcript-segment
   midpoints, about 300 frames per video.
6. Assembly: ManimCE `--save_sections` renders, ffmpeg concat demuxer, `loudnorm` two-pass to
   -16 LUFS via `ffmpeg-normalize`, AAC mux, optional libass burn-in of the Manim `.srt`.

## 9. Unverified items and blocked sources

- OpenAI and ElevenLabs pricing pages, the Kokoro Hugging Face model card, ffmpeg.org filter docs
  (used the FFmpeg GitHub `doc/filters.texi` instead), scenedetect.com docs (used the repository's
  own docs instead), and the Microsoft Q&A thread on edge-tts were DNS-blocked; numbers from web
  search aggregators are marked Low.
- Kokoro CPU real-time factor, Piper voice quality ranking, and whether `kokoro-onnx` exposes token
  timestamps are not measured here.
- YouTube `json3` per-word field names, yt-dlp `info.json` chapter field names, and the exact
  ElevenLabs REST path behind `convert_with_timestamps` are from memory or implied by the SDK.
- Frame-count expectations in section 5 and CPU timing extrapolations in section 4 are estimates to be
  calibrated by the implementation session.
- The kit's `ultracode` skill referenced in the user request was removed from the kit
  (`/home/user/.agents/CHANGELOG.md:58`) and could not be invoked.

