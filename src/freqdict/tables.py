"""Frequency tables (wordforms / lemmas / POS, with subsamples) and n-grams."""
from __future__ import annotations

from collections import Counter

import pandas as pd

from .morphology import annotate
from .text import split_subsamples

Level = str  # "wordform" | "lemma" | "pos"
_LEVEL_INDEX = {"wordform": 0, "lemma": 1, "pos": 2}


def frequency_table(
    tokens: list[str], level: Level, n_subsamples: int = 20
) -> pd.DataFrame:
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
    """Token-level n-gram frequency table with columns ``ngram``, ``total``."""
    if n < 1:
        raise ValueError("n must be >= 1")
    grams = Counter(
        " ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
    )
    return pd.DataFrame(
        [{"ngram": g, "total": c} for g, c in grams.most_common()]
    )


def build_all(
    tokens: list[str],
    n_subsamples: int = 20,
    ngram_sizes: tuple[int, ...] = (2, 3),
) -> dict[str, pd.DataFrame]:
    """Compute every output table in one pass. Keys are sheet/file names."""
    result = {
        "wordforms": frequency_table(tokens, "wordform", n_subsamples),
        "lemmas": frequency_table(tokens, "lemma", n_subsamples),
        "pos": frequency_table(tokens, "pos", n_subsamples),
    }
    for n in ngram_sizes:
        result[f"ngrams_{n}"] = ngram_table(tokens, n)
    return result
