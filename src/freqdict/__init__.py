"""freqdict — frequency dictionaries for Ukrainian text."""

from .tables import build_all, frequency_table, ngram_table
from .text import tokenize

__all__ = ["build_all", "frequency_table", "ngram_table", "tokenize"]
__version__ = "0.1.1"
