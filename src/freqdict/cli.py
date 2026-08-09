"""Command-line interface: build a frequency dictionary from a text file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import export, tables
from .text import tokenize


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="freqdict",
        description=(
            "Build a frequency dictionary (wordforms, lemmas, POS, n-grams) "
            "from a Ukrainian text file."
        ),
    )
    p.add_argument("input", type=Path, help="input .txt file (UTF-8)")
    p.add_argument(
        "-o", "--out", type=Path, default=Path("out"), help="output directory (default: ./out)"
    )
    p.add_argument(
        "--limit", type=int, default=0, help="use only the first N tokens (0 = no limit)"
    )
    p.add_argument(
        "--subsamples",
        type=int,
        default=20,
        help="number of subsamples for frequency columns (default: 20)",
    )
    p.add_argument(
        "--ngrams",
        type=int,
        nargs="*",
        default=[2, 3],
        help="n-gram sizes to compute (default: 2 3)",
    )
    p.add_argument("--xlsx", action="store_true", help="also write a multi-sheet Excel file")
    p.add_argument("--sqlite", action="store_true", help="also write an SQLite database")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        text = args.input.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: cannot read {args.input}: {exc}", file=sys.stderr)
        return 1

    tokens = tokenize(text)
    if not tokens:
        print("error: no Ukrainian tokens found in input", file=sys.stderr)
        return 1
    if args.limit > 0:
        tokens = tokens[: args.limit]

    print(f"tokens: {len(tokens)}")
    result = tables.build_all(
        tokens,
        n_subsamples=args.subsamples,
        ngram_sizes=tuple(args.ngrams),
    )

    csv_paths = export.to_csv(result, args.out)
    written = [str(p) for p in csv_paths]
    if args.xlsx:
        written.append(str(export.to_excel(result, args.out / "freq_dict.xlsx")))
    if args.sqlite:
        written.append(str(export.to_sqlite(result, args.out / "freq_dict.db")))

    print(f"unique wordforms: {len(result['wordforms'])}")
    print(f"unique lemmas:    {len(result['lemmas'])}")
    print("written:")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
