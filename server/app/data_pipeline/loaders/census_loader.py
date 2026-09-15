"""Loads Census / SECC village- or town-level data.

Expected raw file: a CSV/XLSX under app/data_pipeline/raw/, one row per
village/town, exported from Census 2011 / SECC or an Open Government
Data (OGD) mirror of it. Header naming varies a lot between the
different census tables you can download from data.gov.in, so this
loader matches on common aliases instead of requiring one exact header.

Once you've seen the real file, update _COLUMN_ALIASES below to add
whatever header names it actually uses.
"""

from __future__ import annotations

from typing import Any

from app.data_pipeline.loaders._common import read_table, resolve_columns, to_records, to_int

_COLUMN_ALIASES: dict[str, list[str]] = {
    "state": ["state_name", "state", "statename"],
    "district": ["district_name", "district", "dtname"],
    "block": ["block_name", "tehsil", "sub_district_name", "block"],
    "village": ["village_name", "town_name", "vill_name", "village"],
    "population": ["tot_p", "total_population", "population", "tot_pop"],
    "male_population": ["tot_m", "male_population"],
    "female_population": ["tot_f", "female_population"],
    "households": ["no_hh", "number_of_households", "households", "tot_hh"],
    "literates": ["p_lit", "total_literates", "literates"],
    "workers": ["tot_work_p", "total_workers", "workers"],
    "pincode": ["pincode", "pin_code"],
}


def load_census(path: str) -> list[dict]:
    """Load Census/SECC data from `path` into a list of clean records.

    Returns [] if the file is missing, empty, or doesn't look like a
    census export — callers (report_generator / RAG ingest) should
    treat that as "no census data available" rather than a fatal error.
    """
    df = read_table(path)
    if df.empty:
        return []

    column_map = resolve_columns(list(df.columns), _COLUMN_ALIASES)
    if "village" not in column_map and "district" not in column_map:
        # Doesn't look like a census file we recognize — bail out clean
        # instead of returning a pile of unrecognized columns.
        return []

    raw_records = to_records(df)

    records: list[dict[str, Any]] = []
    for row in raw_records:
        record = {
            "state": row.get(column_map.get("state", "")),
            "district": row.get(column_map.get("district", "")),
            "block": row.get(column_map.get("block", "")),
            "village": row.get(column_map.get("village", "")),
            "population": to_int(row.get(column_map.get("population", ""))),
            "male_population": to_int(row.get(column_map.get("male_population", ""))),
            "female_population": to_int(row.get(column_map.get("female_population", ""))),
            "households": to_int(row.get(column_map.get("households", ""))),
            "literates": to_int(row.get(column_map.get("literates", ""))),
            "workers": to_int(row.get(column_map.get("workers", ""))),
            "pincode": row.get(column_map.get("pincode", "")),
        }
        if record["village"] or record["district"]:
            records.append(record)

    return records