"""Synthesize every beat's narration and time its marks within the audio.

Each beat's WAV is cached beside a sidecar of the provider's word times, keyed on the
provider, voice, speed and normalized text, so a rerun re-synthesizes only changed
narration and an edited mark re-aligns against the cached word times.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from dataclasses import asdict
from pathlib import Path

from mtv import common, tts
from mtv import lesson as mtv_lesson

# Kokoro with voice af_heart is the default narration and the fallback of every other provider.
DEFAULT_PROVIDER = "kokoro"
SPEED = 1.0
RETRY_SLEEPS_S = (2.0, 4.0, 8.0)
WARMUP_TEXT = "The quick brown fox jumps over the lazy dog."


def cache_key(provider: str, voice: str, speed: float, text: str) -> str:
    return common.sha256_text("|".join([provider, voice, f"{speed:g}", " ".join(common.normalize_words(text))]))


def voice_for(provider: str, lesson_voice: str | None) -> str:
    """The lesson's voice when it suits ``provider``, else the provider's default ("" for the null one)."""
    if lesson_voice and common.voice_suits(provider, lesson_voice):
        return lesson_voice
    return common.DEFAULT_VOICES.get(provider, "")


def build_provider(name: str, voice: str) -> tts.Provider:
    """The provider ``name``; ValueError for an unknown one or a missing ElevenLabs key."""
    # The key comes from this variable only, and its absence is an environment error to
    # report before any beat, never a failure to retry or fall back from.
    if name == "elevenlabs" and not os.environ.get("ELEVENLABS_API_KEY"):
        raise ValueError("ELEVENLABS_API_KEY is not set")
    return tts.get_provider(name, voice, SPEED)


def build_fallback(provider_name: str) -> tts.Provider | None:
    # Kokoro is the fallback, so it has none itself, and the null provider cannot fail.
    if provider_name in (DEFAULT_PROVIDER, "null"):
        return None
    # Kokoro loads its pipeline on first use, so building it costs nothing until a beat falls back.
    return tts.get_provider(DEFAULT_PROVIDER, common.DEFAULT_VOICES[DEFAULT_PROVIDER])


def synthesize_with_retry(
    provider: tts.Provider,
    text: str,
    out_wav: Path,
    fallback: tts.Provider | None,
    sleeps: tuple[float, ...] = RETRY_SLEEPS_S,
    sleep_fn=time.sleep,
    context: dict[str, str] | None = None,
) -> tuple[list[tts.Word], str, int]:
    """The spoken words, the name of the provider that spoke them, and the retries taken.

    After the last retry fails, ``fallback`` speaks instead, or the failure is raised when
    there is none. ``context`` holds extra keyword arguments for ``provider`` alone (the
    neighboring narration ElevenLabs takes); the fallback speaks the text without them.
    """
    retries = 0
    while True:
        try:
            return provider.synthesize(text, out_wav, **(context or {})), provider.name, retries
        # ConnectionError and TimeoutError are OSError subclasses, as are socket errors.
        except OSError:
            if retries == len(sleeps):
                if fallback is None:
                    raise
                return fallback.synthesize(text, out_wav), fallback.name, retries
            sleep_fn(sleeps[retries])
            retries += 1


def neighbor_context(beats: list[dict], index: int) -> dict[str, str]:
    """The narration either side of beat ``index`` across the whole lesson, for ElevenLabs' prosody."""
    context = {}
    if index > 0:
        context["previous_text"] = beats[index - 1]["narration"]
    if index + 1 < len(beats):
        context["next_text"] = beats[index + 1]["narration"]
    return context


def narrate_beat(
    beat: dict,
    run_dir: Path,
    provider: tts.Provider,
    fallback: tts.Provider | None,
    voice: str,
    speed: float,
    context: dict[str, str] | None = None,
) -> int:
    """Fill ``beat``'s audio, words, duration_s, marks_s and interpolated; return the retries taken."""
    audio, words = f"audio/{beat['id']}.wav", f"audio/{beat['id']}.words.json"
    wav, sidecar = run_dir / audio, run_dir / words
    tokens = _cached_tokens(sidecar, cache_key(provider.name, voice, speed, beat["narration"]), wav)
    retries = 0
    if tokens is None:
        wav.parent.mkdir(exist_ok=True)
        # An interrupted synthesis must not leave a WAV behind a sidecar that still holds its key.
        sidecar.unlink(missing_ok=True)
        tokens, used, retries = synthesize_with_retry(provider, beat["narration"], wav, fallback, context=context)
        # Keyed on the provider that spoke, so a beat that fell back is spoken again by the
        # requested provider on the next run instead of keeping the fallback's audio.
        record = {
            "key": cache_key(used, voice, speed, beat["narration"]),
            "provider": used,
            "tokens": [asdict(token) for token in tokens],
        }
        common.dump_json(record, sidecar)
    script_words = common.normalize_words(beat["narration"])
    marks = beat.get("marks", {})
    duration_s = tts.wav_duration(wav)
    marks_s, interpolated = tts.align_marks(script_words, tokens, marks)
    if interpolated:
        marks_s = tts.interpolate(duration_s, len(script_words), marks)
    beat.update(audio=audio, words=words, duration_s=duration_s, marks_s=marks_s, interpolated=interpolated)
    return retries


def _cached_tokens(sidecar: Path, key: str, wav: Path) -> list[tts.Word] | None:
    """The sidecar's words when it holds ``key`` and the WAV exists, else None."""
    if not (sidecar.exists() and wav.exists()):
        return None
    try:
        cached = common.load_json(sidecar)
        return [tts.Word(**token) for token in cached["tokens"]] if cached["key"] == key else None
    # A sidecar cut short by an interruption is a miss, so the rerun that resumes the run repairs it.
    except (ValueError, KeyError, TypeError):
        return None


def warmup(name: str) -> int:
    """Synthesize one sentence, which makes Kokoro fetch its weights, and print the real-time factor."""
    try:
        provider = build_provider(name, voice_for(name, None))
    except ValueError as exc:
        return common.usage_error(str(exc))
    with tempfile.TemporaryDirectory(prefix="mtv-warmup-") as tmp:
        out_wav = Path(tmp) / "warmup.wav"
        start = time.perf_counter()
        try:
            provider.synthesize(WARMUP_TEXT, out_wav)
        except (OSError, tts.ProviderError) as exc:
            return common.usage_error(f"provider '{name}' failed: {exc}")
        rtf = (time.perf_counter() - start) / tts.wav_duration(out_wav)
    return common.verdict(True, f"warmup {name} rtf={rtf:.3f}")


def main(argv: list[str] | None = None) -> int:
    parser = common.lesson_parser("Synthesize every beat's narration and time its marks.", positional=False)
    parser.add_argument("lesson", type=Path, nargs="?", help="path to lesson.json; omitted with --warmup")
    parser.add_argument("--provider", help="narration provider; default the lesson's, or kokoro with --warmup")
    parser.add_argument("--warmup", action="store_true", help="synthesize one sentence and print the real-time factor")
    args = parser.parse_args(argv)
    if args.warmup:
        if args.lesson is not None:
            return common.usage_error("--warmup takes no lesson")
        return warmup(args.provider or DEFAULT_PROVIDER)
    if args.lesson is None:
        return common.usage_error("lesson.json is required unless --warmup is given")
    lesson, errors = common.load_valid_lesson(args.lesson)
    if errors:
        return common.usage_error("lesson invalid: " + "; ".join(errors))
    name = args.provider or lesson.get("provider") or DEFAULT_PROVIDER
    voice = voice_for(name, lesson.get("voice"))
    try:
        provider = build_provider(name, voice)
        fallback = build_fallback(name)
    except ValueError as exc:
        return common.usage_error(str(exc))
    run_dir = args.lesson.parent
    beats = [beat for _, beat in mtv_lesson.beats(lesson)]
    retries = 0
    for index, beat in enumerate(beats):
        context = neighbor_context(beats, index) if provider.name == "elevenlabs" else None
        try:
            retries += narrate_beat(beat, run_dir, provider, fallback, voice, SPEED, context)
        except tts.ProviderError as exc:
            return common.usage_error(f"provider '{name}' failed: {exc}")
        except OSError as exc:
            return common.usage_error(f"provider '{name}' failed after {len(RETRY_SLEEPS_S)} retries: {exc}")
    for _ in range(retries):
        mtv_lesson.bump(lesson, "provider_retries")
    tools = {"provider": provider.name, "voice": voice}
    if any(common.load_json(run_dir / beat["words"])["provider"] != provider.name for beat in beats):
        tools["fallback"] = fallback.name
    mtv_lesson.mark_done(lesson, "narrate", tools)
    # The stage is done for the provider and voice that spoke, which --provider may have changed
    # from the lesson's: hashed with those, a resume under the lesson's own re-narrates.
    used = {**lesson, "provider": provider.name, "voice": voice}
    lesson["stages"]["narrate"]["inputs_sha256"] = mtv_lesson.stage_inputs(used, "narrate")
    mtv_lesson.save(lesson, args.lesson)
    interpolated = sum(beat["interpolated"] for beat in beats)
    return common.verdict(True, f"narrated {len(beats)} beats, {interpolated} interpolated")


if __name__ == "__main__":
    sys.exit(main())
