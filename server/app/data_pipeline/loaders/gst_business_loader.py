"""Loads GST-registered business data (from an OGD / GST portal export).

Expected raw file: a CSV/XLSX under app/data_pipeline/raw/, one row per
registered business. Header naming differs depending on the source
(GST portal search export vs an OGD dataset), so this loader matches
on common aliases instead of requiring one exact header.

Once you've seen the real file, update _COLUMN_ALIASES below to add
whatever header names it actually uses.
"""

from __future__ import annotations

from typing import Any

from app.data_pipeline.loaders._common import read_table, resolve_columns, to_records

_COLUMN_ALIASES: dict[str, list[str]] = {
    "gstin": ["gstin", "gst_number", "gstin_uin"],
    "legal_name": ["legal_name", "legal_name_of_business"],
    "trade_name": ["trade_name", "trade_name_of_business"],
    "business_type": ["constitution_of_business", "business_type", "nature_of_business"],
    "address": ["address", "principal_place_of_business"],
    "state": ["state", "state_name"],
    "district": ["district", "district_name"],
    "pincode": ["pincode", "pin_code"],
    "registration_date": ["date_of_registration", "registration_date"],
    "status": ["gstin_status", "status"],
}


def load_gst_businesses(path: str) -> list[dict]:
    """Load GST business registration data from `path`.

    Returns [] if the file is missing, empty, or doesn't look like a
    GST export — callers should treat that as "no local competitor
    data available" rather than a fatal error.
    """
    df = read_table(path)
    if df.empty:
        return []

    column_map = resolve_columns(list(df.columns), _COLUMN_ALIASES)
    if "gstin" not in column_map and "trade_name" not in column_map:
        return []

    raw_records = to_records(df)

    records: list[dict[str, Any]] = []
    for row in raw_records:
        record = {
            "gstin": row.get(column_map.get("gstin", "")),
            "legal_name": row.get(column_map.get("legal_name", "")),
            "trade_name": row.get(column_map.get("trade_name", "")),
            "business_type": row.get(column_map.get("business_type", "")),
            "address": row.get(column_map.get("address", "")),
            "state": row.get(column_map.get("state", "")),
            "district": row.get(column_map.get("district", "")),
            "pincode": row.get(column_map.get("pincode", "")),
            "registration_date": row.get(column_map.get("registration_date", "")),
            "status": row.get(column_map.get("status", "")),
        }
        if record["trade_name"] or record["legal_name"]:
            records.append(record)

    return records