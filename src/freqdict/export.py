"""Export frequency tables to CSV, Excel and SQLite."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def to_csv(tables: dict[str, pd.DataFrame], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, df in tables.items():
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        paths.append(path)
    return paths


def to_excel(tables: dict[str, pd.DataFrame], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for name, df in tables.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return out_path


def to_sqlite(tables: dict[str, pd.DataFrame], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(out_path) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, if_exists="replace", index=False)
    return out_path
