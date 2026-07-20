"""Tests for freqdict core modules."""
from pathlib import Path

import pytest

from freqdict import tables
from freqdict.cli import main
from freqdict.morphology import analyze
from freqdict.text import normalize, split_subsamples, tokenize

SAMPLE = "Мова — це зброя. М’ята пахне, будь-хто скаже: мови живуть!"


class TestTokenize:
    def test_basic(self):
        assert tokenize("Слово і діло") == ["слово", "і", "діло"]

    def test_apostrophe_variants_normalized(self):
        assert tokenize("м’ята і м'ята") == ["м'ята", "і", "м'ята"]

    def test_hyphenated_word_kept(self):
        assert "будь-хто" in tokenize(SAMPLE)

    def test_latin_and_digits_dropped(self):
        assert tokenize("Python 3 і мова") == ["і", "мова"]

    def test_normalize_lowercases(self):
        assert normalize("МОВА") == "мова"


class TestSubsamples:
    def test_even_split(self):
        chunks = split_subsamples(list(range(20)), 4)
        assert [len(c) for c in chunks] == [5, 5, 5, 5]

    def test_uneven_split_covers_all(self):
        chunks = split_subsamples(list(range(10)), 3)
        assert sum(len(c) for c in chunks) == 10
        assert len(chunks) == 3

    def test_fewer_tokens_than_subsamples(self):
        chunks = split_subsamples(["а", "б"], 20)
        assert len(chunks) == 2
        assert all(chunks)

    def test_invalid_n(self):
        with pytest.raises(ValueError):
            split_subsamples(["а"], 0)


class TestMorphology:
    def test_lemma_and_pos(self):
        lemma, pos = analyze("мови")
        assert lemma == "мова"
        assert pos == "NOUN"

    def test_unknown_token_does_not_crash(self):
        lemma, pos = analyze("ґзиґзаґ")
        assert isinstance(lemma, str) and isinstance(pos, str)


class TestTables:
    def test_frequency_table_totals(self):
        tokens = tokenize("мова мова слово")
        df = tables.frequency_table(tokens, "wordform", n_subsamples=2)
        top = df.iloc[0]
        assert top["item"] == "мова"
        assert top["total"] == 2
        # subsample columns sum back to total
        sub_cols = [c for c in df.columns if c.startswith("sub_")]
        assert (df[sub_cols].sum(axis=1) == df["total"]).all()

    def test_ngram_table(self):
        df = tables.ngram_table(["а", "б", "а", "б"], 2)
        assert df.iloc[0]["ngram"] == "а б"
        assert df.iloc[0]["total"] == 2

    def test_build_all_keys(self):
        result = tables.build_all(tokenize(SAMPLE), n_subsamples=2)
        assert set(result) == {"wordforms", "lemmas", "pos", "ngrams_2", "ngrams_3"}


class TestCli:
    def test_end_to_end(self, tmp_path: Path):
        src = tmp_path / "in.txt"
        src.write_text(SAMPLE, encoding="utf-8")
        out = tmp_path / "out"
        code = main([str(src), "-o", str(out), "--subsamples", "2",
                     "--xlsx", "--sqlite"])
        assert code == 0
        assert (out / "wordforms.csv").exists()
        assert (out / "freq_dict.xlsx").exists()
        assert (out / "freq_dict.db").exists()

    def test_missing_file(self, tmp_path: Path):
        assert main([str(tmp_path / "nope.txt")]) == 1
