"""Loads NSSO price / consumption data.

Expected raw file: a CSV/XLSX under app/data_pipeline/raw/, one row per
item-price observation from an NSSO survey round (e.g. the Household
Consumption Expenditure Survey) or an OGD mirror of it. Header naming
varies between survey rounds, so this loader matches on common aliases
instead of requiring one exact header.

Once you've seen the real file, update _COLUMN_ALIASES below to add
whatever header names it actually uses.
"""

from __future__ import annotations

from typing import Any

from app.data_pipeline.loaders._common import read_table, resolve_columns, to_records, to_float

_COLUMN_ALIASES: dict[str, list[str]] = {
    "state": ["state", "state_name"],
    "district": ["district", "district_name"],
    "sector": ["sector", "rural_urban"],
    "item_code": ["item_code", "itemcode"],
    "item_name": ["item_name", "item_description", "item"],
    "price": ["price", "avg_price", "unit_value", "value"],
    "quantity": ["quantity", "qty"],
    "unit": ["unit", "unit_of_measurement"],
    "month": ["month"],
    "year": ["year", "survey_year"],
}


def load_nsso_prices(path: str) -> list[dict]:
    """Load NSSO item-price data from `path`.

    Returns [] if the file is missing, empty, or doesn't look like an
    NSSO price export — callers should treat that as "no price
    benchmark data available" rather than a fatal error.
    """
    df = read_table(path)
    if df.empty:
        return []

    column_map = resolve_columns(list(df.columns), _COLUMN_ALIASES)
    if "item_name" not in column_map and "price" not in column_map:
        return []

    raw_records = to_records(df)

    records: list[dict[str, Any]] = []
    for row in raw_records:
        record = {
            "state": row.get(column_map.get("state", "")),
            "district": row.get(column_map.get("district", "")),
            "sector": row.get(column_map.get("sector", "")),
            "item_code": row.get(column_map.get("item_code", "")),
            "item_name": row.get(column_map.get("item_name", "")),
            "price": to_float(row.get(column_map.get("price", ""))),
            "quantity": to_float(row.get(column_map.get("quantity", ""))),
            "unit": row.get(column_map.get("unit", "")),
            "month": row.get(column_map.get("month", "")),
            "year": row.get(column_map.get("year", "")),
        }
        if record["item_name"] or record["price"] is not None:
            records.append(record)

    return records