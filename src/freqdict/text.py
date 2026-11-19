"""Text cleaning and tokenization for Ukrainian text."""

from __future__ import annotations

import re

# Apostrophe look-alikes (’ ʼ ‘ ` ´ ′ ʹ ＇) between two letters. pymorphy3-dicts-uk
# knows only the ASCII apostrophe, so any other variant makes a word unknown and
# its lemma wrong. Quotes next to a word (‘цитата’) are not between letters and
# stay untouched.
_APOSTROPHE_VARIANTS = re.compile(
    r"(?<=[^\W\d_])[\u2019\u02BC\u2018\u0060\u00B4\u2032\u02B9\uFF07](?=[^\W\d_])"
)
# Any Cyrillic word (Ukrainian letters plus ъ, ы, э, ё), apostrophe and hyphen
# inside words. The wider class matters: matching only Ukrainian letters would
# cut a Russian word like "объект" into the fragments "об" and "ект" and count
# them as Ukrainian tokens. Words are matched whole, then filtered.
_WORD = re.compile(r"[а-яёєіїґ]+(?:['\-][а-яёєіїґ]+)*", re.IGNORECASE)
# Letters that do not occur in Ukrainian orthography
_NON_UKRAINIAN = re.compile(r"[ъыэё]", re.IGNORECASE)
# Sentence-final punctuation; n-grams are not allowed to span it
_SENTENCE_END = re.compile(r"[.!?\u2026]+")


def normalize_apostrophes(text: str) -> str:
    """Replace intra-word apostrophe variants with the ASCII apostrophe (U+0027)."""
    return _APOSTROPHE_VARIANTS.sub("'", text)


def normalize(text: str) -> str:
    """Lowercase and normalize apostrophe variants."""
    return normalize_apostrophes(text).lower()


def tokenize(text: str) -> list[str]:
    """Extract Ukrainian word tokens from raw text.

    Keeps apostrophes (м'ята) and in-word hyphens (будь-хто),
    drops digits, latin words, punctuation and whole words containing
    letters absent from Ukrainian (ъ, ы, э, ё).
    """
    return [w for w in _WORD.findall(normalize(text)) if not _NON_UKRAINIAN.search(w)]


def tokenize_sentences(text: str) -> list[list[str]]:
    """Tokenize ``text`` sentence by sentence; empty sentences are dropped.

    Sentence boundaries are ``.``, ``!``, ``?`` and ``…``. Abbreviations
    ("т. д.") split too, which only costs n-grams across that point.
    """
    return [tokens for part in _SENTENCE_END.split(text) if (tokens := tokenize(part))]


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
