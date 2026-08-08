# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
