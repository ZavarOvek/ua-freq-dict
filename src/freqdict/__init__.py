"""freqdict — frequency dictionaries for Ukrainian text."""

from .tables import build_all, frequency_table, ngram_table, segmented_ngram_table
from .text import tokenize, tokenize_sentences

__all__ = [
    "build_all",
    "frequency_table",
    "ngram_table",
    "segmented_ngram_table",
    "tokenize",
    "tokenize_sentences",
]
__version__ = "0.1.1"
