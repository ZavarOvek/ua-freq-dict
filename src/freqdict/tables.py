"""Frequency tables (wordforms / lemmas / POS, with subsamples) and n-grams."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from .morphology import annotate
from .text import split_subsamples

Level = str  # "wordform" | "lemma" | "pos"
_LEVEL_INDEX = {"wordform": 0, "lemma": 1, "pos": 2}


def frequency_table(tokens: list[str], level: Level, n_subsamples: int = 20) -> pd.DataFrame:
    """Build a frequency table for one annotation level.

    Columns: ``item``, ``total`` and one ``sub_i`` column per subsample.
    Rows are sorted by total frequency, descending.
    """
    idx = _LEVEL_INDEX[level]
    annotated = annotate(tokens)
    items = [triple[idx] for triple in annotated]

    total = Counter(items)
    chunks = split_subsamples(items, n_subsamples)
    sub_counts = [Counter(chunk) for chunk in chunks]

    rows = []
    for item, freq in total.most_common():
        row = {"item": item, "total": freq}
        for i, counter in enumerate(sub_counts, start=1):
            row[f"sub_{i}"] = counter.get(item, 0)
        rows.append(row)
    return pd.DataFrame(rows)


def ngram_table(tokens: list[str], n: int) -> pd.DataFrame:
    """Token-level n-gram frequency table with columns ``ngram``, ``total``.

    Treats ``tokens`` as one unbroken sequence. To keep n-grams inside
    sentences, use :func:`segmented_ngram_table`.
    """
    return segmented_ngram_table([tokens], n)


def segmented_ngram_table(segments: list[list[str]], n: int) -> pd.DataFrame:
    """N-gram table where no n-gram crosses a segment (sentence) boundary."""
    if n < 1:
        raise ValueError("n must be >= 1")
    grams: Counter[str] = Counter()
    for seg in segments:
        grams.update(" ".join(seg[i : i + n]) for i in range(len(seg) - n + 1))
    return pd.DataFrame(
        [{"ngram": g, "total": c} for g, c in grams.most_common()], columns=["ngram", "total"]
    )


def build_all(
    tokens: list[str],
    n_subsamples: int = 20,
    ngram_sizes: tuple[int, ...] = (2, 3),
    sentences: list[list[str]] | None = None,
) -> dict[str, pd.DataFrame]:
    """Compute every output table in one pass. Keys are sheet/file names.

    If ``sentences`` is given (see :func:`freqdict.text.tokenize_sentences`),
    n-grams are counted within sentences only; ``tokens`` still drives the
    frequency tables. Without it, n-grams run over ``tokens`` as one stream.
    """
    segments = sentences if sentences is not None else [tokens]
    result = {
        "wordforms": frequency_table(tokens, "wordform", n_subsamples),
        "lemmas": frequency_table(tokens, "lemma", n_subsamples),
        "pos": frequency_table(tokens, "pos", n_subsamples),
    }
    for n in ngram_sizes:
        result[f"ngrams_{n}"] = segmented_ngram_table(segments, n)
    return result
