"""Lemmatization and POS tagging via pymorphy3 with per-token caching."""

from __future__ import annotations

from functools import lru_cache

import pymorphy3

_analyzer: pymorphy3.MorphAnalyzer | None = None


def _get_analyzer() -> pymorphy3.MorphAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = pymorphy3.MorphAnalyzer(lang="uk")
    return _analyzer


@lru_cache(maxsize=200_000)
def analyze(token: str) -> tuple[str, str]:
    """Return ``(lemma, pos)`` for a single token.

    POS uses pymorphy3 / OpenCorpora tags (NOUN, VERB, ADJF, ...);
    unknown tags are reported as ``UNKN``.
    """
    parse = _get_analyzer().parse(token)[0]
    lemma = parse.normal_form
    pos = str(parse.tag.POS) if parse.tag.POS is not None else "UNKN"
    return lemma, pos


def annotate(tokens: list[str]) -> list[tuple[str, str, str]]:
    """Return ``(wordform, lemma, pos)`` triples for a token list."""
    return [(t, *analyze(t)) for t in tokens]
