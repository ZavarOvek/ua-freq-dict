# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Fixed
- N-grams no longer span sentence boundaries: the CLI tokenizes sentence by
  sentence (`.`, `!`, `?`, `…`) and counts n-grams inside each. New
  `tokenize_sentences()` and `segmented_ngram_table()`; `build_all()` takes an
  optional `sentences=` argument. `ngram_table()` keeps its old behaviour.
- A word containing `ъ`, `ы`, `э` or `ё` is dropped whole instead of being cut
  into Ukrainian-looking fragments (`объект` used to yield `об` and `ект`).
- `--subsamples 0` and `--ngrams 0` are rejected by argparse with exit code 2
  instead of a traceback.
- `--sqlite` export closes its connection; the database file is no longer
  held open (locked on Windows) after the export returns.

### Changed
- Adopted `ruff format` as the project formatter; the whole tree was
  reformatted in a single dedicated commit (see `.git-blame-ignore-revs`).
- `E501` disabled in `ruff check`: line length is the formatter's job, and
  the formatter cannot split string literals anyway.
- CI lint job now also runs `ruff format --check .`.

## [0.1.1] - 2026-08-08

### Added
- GitHub Actions CI: `ruff` lint job and a `pytest` matrix on Python 3.10-3.12.
- Ruff configuration in `pyproject.toml` (`RUF001-003` disabled: they flag
  Cyrillic letters as ambiguous look-alikes of Latin ones, which is a false
  positive in a project about Ukrainian text).
- Package metadata: `keywords`, `classifiers` and `[project.urls]`.
- Status badges in both READMEs.

### Changed
- `license` migrated to the PEP 639 SPDX form (`license = "MIT"` +
  `license-files`); build now requires `setuptools>=77`.
- Import order normalized by ruff; no behaviour changes.

## [0.1.0] - 2026-07-20

### Added
- Initial release: frequency dictionaries for Ukrainian text.
- Tokenization with apostrophe normalization and in-word hyphen support;
  digits and Latin words filtered out.
- Lemmatization and POS tagging via `pymorphy3`, with caching.
- Wordform / lemma / POS frequency tables with per-subsample columns.
- Token-level n-grams of arbitrary size (default: bigrams and trigrams).
- Export to CSV (UTF-8 BOM), multi-sheet XLSX and SQLite.
- `freqdict` CLI entry point and `tokenize()` / `build_all()` library API.
- Test suite (pytest).
