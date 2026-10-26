"""Narration providers, and the times of a beat's marks within its narration.

A provider writes a beat's WAV and returns the words it spoke with their times. A mark
names a word of the script, so its time is that of the spoken word matched to it, and an
even spread of the script's words over the audio stands in when no match exists.
"""

from __future__ import annotations

import importlib
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from . import common

# Kokoro's native rate; every provider writes it, so beats join without resampling.
_SAMPLE_RATE_HZ = 24000


@dataclass(frozen=True)
class Word:
    """A spoken token and its span in the beat's WAV, in seconds from the start."""

    text: str
    start_s: float
    end_s: float


class Provider(Protocol):
    name: str

    def synthesize(self, text: str, out_wav: Path) -> list[Word]:
        """Write ``text`` spoken as a 24 kHz mono WAV; ``[]`` means no timestamps."""
        ...


class NullProvider:
    """Silence lasting as long as ``text`` takes at WORDS_PER_MINUTE, with evenly spaced words."""

    name = "null"

    def synthesize(self, text: str, out_wav: Path) -> list[Word]:
        words = common.normalize_words(text)
        word_s = 60 / common.WORDS_PER_MINUTE
        _write_wav(out_wav, bytes(2 * round(len(words) * word_s * _SAMPLE_RATE_HZ)))
        return [Word(word, i * word_s, (i + 1) * word_s) for i, word in enumerate(words)]


def _transport_errors() -> tuple[type[Exception], ...]:
    """The transport error of each HTTP client huggingface_hub may use (it moved from httpx to httpx2)."""
    found = []
    for module in ("httpx2", "httpx"):
        try:
            found.append(importlib.import_module(module).TransportError)
        except ImportError:
            pass
    return tuple(found)


class KokoroProvider:
    """Kokoro-82M, offline once its weights are cached, with per-token times from its duration predictor."""

    name = "kokoro"

    def __init__(self, voice: str = "af_heart", speed: float = 1.0, lang_code: str = "a") -> None:
        self.voice, self.speed, self.lang_code = voice, speed, lang_code
        self._pipeline = None

    def _get_pipeline(self):
        # Built on first use, so a provider that only stands by as the fallback costs nothing.
        if self._pipeline is None:
            # Through hf-xet's Rust client the weight download bypasses Python logging, so
            # the hosts it reaches could not be told apart from the ones M0 recorded.
            os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
            import kokoro
            from huggingface_hub import errors as hub_errors

            # The model and voice weights download on first use. huggingface_hub's own HTTP
            # errors are OSErrors, but a refused connection surfaces as its HTTP client's
            # TransportError, which is not; either becomes the ConnectionError the scripts
            # treat as a network failure. Anything else (a corrupt cache, a G2P bug) and a
            # name the hub does not have (a misspelled voice) keep their own type.
            try:
                pipeline = kokoro.KPipeline(lang_code=self.lang_code, repo_id="hexgrad/Kokoro-82M")
                pipeline.load_voice(self.voice)
            except hub_errors.EntryNotFoundError as exc:
                if not isinstance(exc, hub_errors.LocalEntryNotFoundError):
                    raise
                raise ConnectionError(f"kokoro could not load its weights: {exc}") from exc
            except (OSError, *_transport_errors()) as exc:
                raise ConnectionError(f"kokoro could not load its weights: {exc}") from exc
            self._pipeline = pipeline
        return self._pipeline

    def synthesize(self, text: str, out_wav: Path) -> list[Word]:
        import numpy
        import soundfile

        chunks, words, offset_s = [], [], 0.0
        # The pipeline splits long text into chunks, each timed from its own start.
        for result in self._get_pipeline()(text, voice=self.voice, speed=self.speed):
            if result.audio is None:
                continue
            audio = result.audio.numpy()
            words += [
                Word(token.text, offset_s + token.start_ts, offset_s + token.end_ts)
                for token in result.tokens or []
                if token.start_ts is not None and token.end_ts is not None
            ]
            chunks.append(audio)
            offset_s += len(audio) / _SAMPLE_RATE_HZ
        soundfile.write(str(out_wav), numpy.concatenate(chunks) if chunks else numpy.zeros(0), _SAMPLE_RATE_HZ)
        return words


class ElevenLabsProvider:
    """ElevenLabs over its API, timed per character, with the neighboring beats' text passed for prosody."""

    name = "elevenlabs"

    def __init__(self, voice: str, speed: float = 1.0) -> None:
        self.voice, self.speed = voice, speed

    def _client(self):
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            # Not an OSError, so a missing key is never retried or answered with the fallback.
            raise RuntimeError("ELEVENLABS_API_KEY is not set")
        from elevenlabs.client import ElevenLabs

        return ElevenLabs(api_key=key)

    def synthesize(
        self, text: str, out_wav: Path, previous_text: str | None = None, next_text: str | None = None
    ) -> list[Word]:
        import base64

        # First, so a missing key is reported as such even where the SDK is not installed.
        client = self._client()
        from elevenlabs.core.api_error import ApiError

        # Unset neighbors are left out, not sent as null: the SDK omits only its own sentinel.
        options = {k: v for k, v in (("previous_text", previous_text), ("next_text", next_text)) if v is not None}
        if self.speed != 1.0:
            from elevenlabs.types import VoiceSettings

            options["voice_settings"] = VoiceSettings(speed=self.speed)
        try:
            response = client.text_to_speech.convert_with_timestamps(
                voice_id=self.voice, text=text, output_format="pcm_24000", **options
            )
        except _transport_errors() as exc:
            raise ConnectionError(f"elevenlabs unreachable: {exc}") from exc
        except ApiError as exc:
            # Rate limits and server errors pass; any other status is the request's fault.
            if exc.status_code == 429 or (exc.status_code or 0) >= 500:
                raise ConnectionError(f"elevenlabs answered {exc.status_code}") from exc
            raise
        _write_wav(out_wav, base64.b64decode(response.audio_base_64))
        alignment = response.normalized_alignment
        if alignment is None:
            return []
        return words_from_characters(
            alignment.characters, alignment.character_start_times_seconds, alignment.character_end_times_seconds
        )


def _write_wav(path: Path, frames: bytes) -> None:
    """Write 16-bit little-endian mono PCM at the shared rate."""
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(_SAMPLE_RATE_HZ)
        wav.writeframes(frames)


def get_provider(name: str, voice: str = "af_heart", speed: float = 1.0) -> Provider:
    """The provider ``name``; ``voice`` and ``speed`` configure a speaking one, and the null one has neither."""
    if name == "null":
        return NullProvider()
    if name == "kokoro":
        return KokoroProvider(voice, speed)
    if name == "elevenlabs":
        return ElevenLabsProvider(voice, speed)
    raise ValueError(f"unknown provider '{name}'")


def token_words(tokens: list[Word]) -> list[tuple[str, Word]]:
    """Each token's normalized words, paired with the token.

    A provider's token can hold several script words ("eighty-four") or none (a
    punctuation token), so matching happens word by word.
    """
    return [(word, token) for token in tokens for word in common.normalize_words(token.text)]


def lcs_align(a: list[str], b: list[str]) -> dict[int, int]:
    """Index in ``a`` to index in ``b`` for a longest common subsequence.

    Read left to right, two equal words match as soon as both are reached, so a repeated
    word pairs with the first of its twins.
    """
    # suffix[i][j] is the length of a longest common subsequence of a[i:] and b[j:].
    suffix = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            suffix[i][j] = suffix[i + 1][j + 1] + 1 if a[i] == b[j] else max(suffix[i + 1][j], suffix[i][j + 1])
    pairs: dict[int, int] = {}
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            pairs[i] = j
            i += 1
            j += 1
        elif suffix[i + 1][j] >= suffix[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def align_marks(
    script_words: list[str], tokens: list[Word], marks: dict[str, int]
) -> tuple[dict[str, float], bool]:
    """Each mark's time: the start of the token its script word matched.

    When any mark's word matched no token, the result is ``({}, True)``, meaning the
    beat's marks need interpolating.
    """
    spoken = token_words(tokens)
    matched = lcs_align(script_words, [word for word, _ in spoken])
    if not all(index in matched for index in marks.values()):
        return {}, True
    return {name: spoken[matched[index]][1].start_s for name, index in marks.items()}, False


def interpolate(duration_s: float, n_words: int, marks: dict[str, int]) -> dict[str, float]:
    """Each mark's time with the words spread evenly over ``duration_s``: its word's midpoint."""
    if n_words == 0:
        raise ValueError("cannot interpolate marks over a narration of 0 words")
    return {name: duration_s * (index + 0.5) / n_words for name, index in marks.items()}


def words_from_characters(characters: list[str], starts: list[float], ends: list[float]) -> list[Word]:
    """Timed characters grouped into words at whitespace, each word spanning its first to last character."""
    groups: list[list[tuple[str, float, float]]] = [[]]
    for timed in zip(characters, starts, ends, strict=True):
        if timed[0].isspace():
            groups.append([])
        else:
            groups[-1].append(timed)
    return [Word("".join(c for c, _, _ in group), group[0][1], group[-1][2]) for group in groups if group]


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()
