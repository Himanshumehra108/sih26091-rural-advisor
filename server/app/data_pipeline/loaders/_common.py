"""Shared helpers for the data_pipeline loaders.

Every loader in this package follows the same contract:

    def load_x(path: str) -> list[dict]

This module centralizes the boring, repetitive part (finding the file,
reading csv/xlsx/json, normalizing column names, turning NaN into
None) so each loader only has to worry about the columns that are
specific to its own dataset.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def read_table(path: str) -> pd.DataFrame:
    """Read a csv / xlsx / xls / json file into a DataFrame.

    Never raises. Returns an empty DataFrame if the file is missing,
    empty, or unparsable, so one bad/absent raw file degrades that
    loader to an empty list instead of crashing the whole pipeline.
    """
    file_path = Path(path)

    if not file_path.exists():
        logger.warning("data_pipeline: file not found: %s", file_path)
        return pd.DataFrame()

    suffix = file_path.suffix.lower()

    try:
        if suffix == ".csv":
            df = pd.read_csv(file_path, dtype=str, keep_default_na=True)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(file_path, dtype=str)
        elif suffix == ".json":
            df = pd.read_json(file_path, dtype=False)
        else:
            logger.warning("data_pipeline: unsupported file type: %s", file_path)
            return pd.DataFrame()
    except Exception:
        logger.exception("data_pipeline: failed to read %s", file_path)
        return pd.DataFrame()

    return _normalize_columns(df)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """lower_snake_case every column name so aliasing logic can rely on it."""
    df = df.rename(
        columns=lambda c: str(c).strip().lower().replace(" ", "_").replace("-", "_")
    )
    return df


def to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """DataFrame -> list[dict], with NaN/NaT turned into None and
    whitespace-only strings stripped to None."""
    if df.empty:
        return []

    df = df.where(pd.notnull(df), None)
    raw_records = df.to_dict(orient="records")

    cleaned: list[dict[str, Any]] = []
    for row in raw_records:
        clean_row: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, str):
                value = value.strip() or None
            clean_row[key] = value
        cleaned.append(clean_row)
    return cleaned


def resolve_columns(
    columns: list[str], column_aliases: dict[str, list[str]]
) -> dict[str, str]:
    """Map canonical_field -> actual column name found in this file.

    `column_aliases` is {canonical_name: [possible_raw_header, ...]}.
    The first alias that matches an actual column wins.
    """
    resolved: dict[str, str] = {}
    for canonical, aliases in column_aliases.items():
        for alias in aliases:
            if alias in columns:
                resolved[canonical] = alias
                break
    return resolved


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def to_int(value: Any) -> int | None:
    f = to_float(value)
    return int(f) if f is not None else None