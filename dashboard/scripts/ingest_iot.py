#!/usr/bin/env python3
"""Ingestao CSV -> SQLite (IR ALEM 1 - Humberto)."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from paths import DEFAULT_CSV, DEFAULT_DB, SCHEMA_SQL, TASK_ROOT

REQUIRED_COLUMNS = [
    "data_hora",
    "talhao_id",
    "umidade_solo",
    "ph_solo",
    "nitrogenio",
    "fosforo",
    "potassio",
    "temperatura_c",
    "rendimento_t_ha",
    "irrigacao_sugerida_l",
]


def validate_dataframe(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(missing)}")

    if df.empty:
        raise ValueError("CSV sem linhas para ingestao")

    null_counts = df[REQUIRED_COLUMNS].isna().sum()
    invalid = null_counts[null_counts > 0]
    if not invalid.empty:
        details = ", ".join(f"{col}={count}" for col, count in invalid.items())
        raise ValueError(f"CSV contem valores nulos em colunas obrigatorias: {details}")


def ingest(csv_path: Path = DEFAULT_CSV, db_path: Path = DEFAULT_DB) -> int:
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV ausente: {csv_path}. Rode: python scripts/generate_dataset.py")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if SCHEMA_SQL.is_file():
        schema = SCHEMA_SQL.read_text(encoding="utf-8")
    else:
        schema = """
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            talhao_id INTEGER,
            umidade_solo REAL,
            ph_solo REAL,
            nitrogenio REAL,
            fosforo REAL,
            potassio REAL,
            temperatura_c REAL,
            rendimento_t_ha REAL,
            irrigacao_sugerida_l REAL
        );
        """

    df = pd.read_csv(csv_path)
    validate_dataframe(df)
    df = df[REQUIRED_COLUMNS]

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema)
        conn.execute("DELETE FROM leituras_sensores")
        df.to_sql("leituras_sensores", conn, if_exists="append", index=False)
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM leituras_sensores").fetchone()[0]
        talhoes = conn.execute("SELECT COUNT(DISTINCT talhao_id) FROM leituras_sensores").fetchone()[0]
    finally:
        conn.close()

    print(f"[ok] {count} linhas em {db_path.relative_to(TASK_ROOT)}")
    print(f"[ok] {talhoes} talhoes distintos ingeridos")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestao IoT -> SQLite")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    ingest(args.csv, args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
