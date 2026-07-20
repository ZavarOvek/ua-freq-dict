"""Text cleaning and tokenization for Ukrainian text."""
from __future__ import annotations

import re

# Normalize all apostrophe variants to the standard Ukrainian apostrophe
_APOSTROPHES = re.compile(r"[\u2019\u02BC\u0060\u00B4']")
# Ukrainian letters (incl. ґ, є, і, ї), apostrophe and hyphen inside words
_TOKEN = re.compile(r"[а-щьюяєіїґ]+(?:['\-][а-щьюяєіїґ]+)*", re.IGNORECASE)


def normalize(text: str) -> str:
    """Lowercase and normalize apostrophe variants."""
    return _APOSTROPHES.sub("'", text).lower()


def tokenize(text: str) -> list[str]:
    """Extract Ukrainian word tokens from raw text.

    Keeps apostrophes (м'ята) and in-word hyphens (будь-хто),
    drops digits, latin words and punctuation.
    """
    return _TOKEN.findall(normalize(text))


def split_subsamples(tokens: list[str], n_subsamples: int) -> list[list[str]]:
    """Split a token list into ``n_subsamples`` near-equal contiguous chunks.

    If there are fewer tokens than subsamples, returns one chunk per token
    group that exists (never empty chunks).
    """
    if n_subsamples < 1:
        raise ValueError("n_subsamples must be >= 1")
    total = len(tokens)
    if total == 0:
        return []
    n = min(n_subsamples, total)
    base, extra = divmod(total, n)
    chunks, start = [], 0
    for i in range(n):
        size = base + (1 if i < extra else 0)
        chunks.append(tokens[start : start + size])
        start += size
    return chunks
