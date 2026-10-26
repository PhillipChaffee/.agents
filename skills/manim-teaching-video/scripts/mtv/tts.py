"""Narration providers, and the times of a beat's marks within its narration.

A provider writes a beat's WAV and returns the words it spoke with their times. A mark
names a word of the script, so its time is that of the spoken word matched to it, and an
even spread of the script's words over the audio stands in when no match exists.
"""

from __future__ import annotations

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
        with wave.open(str(out_wav), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(_SAMPLE_RATE_HZ)
            wav.writeframes(bytes(2 * round(len(words) * word_s * _SAMPLE_RATE_HZ)))
        return [Word(word, i * word_s, (i + 1) * word_s) for i, word in enumerate(words)]


def get_provider(name: str, voice: str = "af_heart", speed: float = 1.0) -> Provider:
    """The provider ``name``; ``voice`` and ``speed`` configure a speaking one, and the null one has neither."""
    if name == "null":
        return NullProvider()
    if name in ("kokoro", "elevenlabs"):
        raise ValueError(f"provider '{name}' not implemented yet")
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
