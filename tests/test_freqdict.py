"""Tests for freqdict core modules."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from freqdict import tables
from freqdict.cli import main
from freqdict.morphology import analyze
from freqdict.text import (
    normalize,
    normalize_apostrophes,
    split_subsamples,
    tokenize,
    tokenize_sentences,
)

SAMPLE = "Мова — це зброя. М’ята пахне, будь-хто скаже: мови живуть!"


APOSTROPHE_VARIANTS = [
    "\u2019",
    "\u02bc",
    "\u2018",
    "\u0060",
    "\u00b4",
    "\u2032",
    "\u02b9",
    "\uff07",
]


class TestTokenize:
    def test_basic(self):
        assert tokenize("Слово і діло") == ["слово", "і", "діло"]

    def test_apostrophe_variants_normalized(self):
        assert tokenize("м’ята і м'ята") == ["м'ята", "і", "м'ята"]

    @pytest.mark.parametrize("variant", APOSTROPHE_VARIANTS)
    def test_every_apostrophe_variant_normalized(self, variant: str):
        assert normalize_apostrophes(f"м{variant}ясо") == "м'ясо"
        assert tokenize(f"М{variant}ясо") == ["м'ясо"]

    @pytest.mark.parametrize("variant", APOSTROPHE_VARIANTS)
    def test_quotes_around_words_untouched(self, variant: str):
        quoted = f"{variant}цитата{variant}"
        assert normalize_apostrophes(quoted) == quoted
        assert tokenize(quoted) == ["цитата"]

    def test_hyphenated_word_kept(self):
        assert "будь-хто" in tokenize(SAMPLE)

    def test_latin_and_digits_dropped(self):
        assert tokenize("Python 3 і мова") == ["і", "мова"]

    def test_normalize_lowercases(self):
        assert normalize("МОВА") == "мова"

    def test_non_ukrainian_cyrillic_word_dropped_whole(self):
        # Without the whole-word filter "объект" became the tokens "об", "ект".
        assert tokenize("Він сказав: объект, это, всё") == ["він", "сказав"]

    def test_sentences(self):
        assert tokenize_sentences("Прийшла весна. Сонце світить!  ...") == [
            ["прийшла", "весна"],
            ["сонце", "світить"],
        ]


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

    @pytest.mark.parametrize("variant", APOSTROPHE_VARIANTS)
    def test_apostrophe_variant_has_same_lemma_as_ascii(self, variant: str):
        (variant_token,) = tokenize(f"м{variant}ясо")
        assert analyze(variant_token) == analyze("м'ясо")
        assert analyze("з'їв")[0] == "з'їсти"
        assert analyze(tokenize(f"з{variant}їв")[0]) == analyze("з'їв")

    def test_variants_merge_in_frequency_tables(self):
        tokens = tokenize("м’ясо мʼясо м'ясо")
        result = tables.build_all(tokens, n_subsamples=1)
        wordforms, lemmas = result["wordforms"], result["lemmas"]
        assert wordforms["item"].tolist() == ["м'ясо"]
        assert wordforms["total"].tolist() == [3]
        assert len(lemmas) == 1
        assert lemmas["total"].tolist() == [3]

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

    def test_segmented_ngrams_do_not_cross_sentences(self):
        df = tables.segmented_ngram_table([["прийшла", "весна"], ["сонце", "світить"]], 2)
        assert sorted(df["ngram"]) == ["прийшла весна", "сонце світить"]

    def test_segmented_ngrams_short_segment_yields_empty_table(self):
        df = tables.segmented_ngram_table([["одне"]], 2)
        assert df.empty
        assert list(df.columns) == ["ngram", "total"]

    def test_build_all_uses_sentences_for_ngrams(self):
        sentences = tokenize_sentences("Прийшла весна. Сонце світить.")
        tokens = [t for s in sentences for t in s]
        result = tables.build_all(tokens, n_subsamples=2, ngram_sizes=(2,), sentences=sentences)
        assert "весна сонце" not in set(result["ngrams_2"]["ngram"])

    def test_build_all_keys(self):
        result = tables.build_all(tokenize(SAMPLE), n_subsamples=2)
        assert set(result) == {"wordforms", "lemmas", "pos", "ngrams_2", "ngrams_3"}


class TestCli:
    def test_end_to_end(self, tmp_path: Path):
        src = tmp_path / "in.txt"
        src.write_text(SAMPLE, encoding="utf-8")
        out = tmp_path / "out"
        code = main([str(src), "-o", str(out), "--subsamples", "2", "--xlsx", "--sqlite"])
        assert code == 0
        assert (out / "wordforms.csv").exists()
        assert (out / "freq_dict.xlsx").exists()
        assert (out / "freq_dict.db").exists()

    def test_missing_file(self, tmp_path: Path):
        assert main([str(tmp_path / "nope.txt")]) == 1

    def test_cli_ngrams_stay_inside_sentences(self, tmp_path: Path):
        src = tmp_path / "in.txt"
        src.write_text("Прийшла весна. Сонце світить.", encoding="utf-8")
        out = tmp_path / "out"
        assert main([str(src), "-o", str(out), "--subsamples", "2", "--ngrams", "2"]) == 0
        text = (out / "ngrams_2.csv").read_text(encoding="utf-8-sig")
        assert "весна сонце" not in text
        assert "прийшла весна" in text

    def test_cli_limit_counts_tokens_across_sentences(self, tmp_path: Path):
        src = tmp_path / "in.txt"
        src.write_text("Прийшла весна. Сонце світить.", encoding="utf-8")
        out = tmp_path / "out"
        assert main([str(src), "-o", str(out), "--limit", "3", "--subsamples", "1"]) == 0
        text = (out / "wordforms.csv").read_text(encoding="utf-8-sig")
        assert "сонце" in text
        assert "світить" not in text

    @pytest.mark.parametrize("flag", ["--subsamples", "--ngrams"])
    def test_cli_rejects_non_positive(self, tmp_path: Path, flag: str):
        src = tmp_path / "in.txt"
        src.write_text(SAMPLE, encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            main([str(src), "-o", str(tmp_path / "out"), flag, "0"])
        assert exc.value.code == 2

    def test_sqlite_file_released(self, tmp_path: Path):
        src = tmp_path / "in.txt"
        src.write_text(SAMPLE, encoding="utf-8")
        out = tmp_path / "out"
        assert main([str(src), "-o", str(out), "--subsamples", "2", "--sqlite"]) == 0
        db = out / "freq_dict.db"
        # Renaming an open file fails on Windows; everywhere it proves the
        # tables were committed and readable after the export returned.
        moved = db.rename(tmp_path / "moved.db")
        with closing(sqlite3.connect(moved)) as conn:
            (n,) = conn.execute("SELECT COUNT(*) FROM wordforms").fetchone()
        assert n > 0
