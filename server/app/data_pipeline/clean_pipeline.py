"""
clean_pipeline.py
------------------
Step 1: clean and standardize government-style crop yield datasets.

Real government datasets (Census, NSSO, Open Government Data) commonly
have these problems, all reproduced in raw/district_yield_2021.csv and
raw/district_yield_2022.csv on purpose:

1. A junk title row above the real header ("DISTRICT DATA - CROP YIELD
   REPORT") that breaks a naive `pd.read_csv(path)`.
2. Column names that drift between years/sources: "District Name" vs
   "District", "Yield (quintal/hectare)" vs "Yield (kg/hectare)" --
   same meaning, different labels AND different units.
3. Inconsistent casing/whitespace in category columns ("Karnal" vs
   "karnal") that makes naive groupby() treat them as different groups.
4. Missing values encoded inconsistently: empty string, "N/A", actual
   NaN.
5. Exact duplicate rows (double-counted entries).

This script fixes all of that and produces one clean, unit-consistent
DataFrame ready to feed downstream (e.g. into rag/ as structured
context, or into geo_service.py-linked advisory logic).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent / "raw"
OUTPUT_PATH = Path(__file__).parent / "clean_district_yield.csv"

COLUMN_ALIASES = {
    "state": "state",
    "district name": "district",
    "district": "district",
    "crop": "crop",
    "yield (quintal/hectare)": "yield_qtl_per_ha",
    "yield (kg/hectare)": "yield_kg_per_ha",
    "area (hectares)": "area_ha",
    "area (ha)": "area_ha",
    "year": "year",
}

NA_VALUES = ["N/A", "n/a", "NA", "", "-", "NULL"]


def _read_messy_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=1, na_values=NA_VALUES, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={c: COLUMN_ALIASES.get(c, c) for c in df.columns})
    return df


def _unify_yield_units(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "yield_kg_per_ha" in df.columns:
        converted = df["yield_kg_per_ha"] / 100.0
        if "yield_qtl_per_ha" in df.columns:
            df["yield_qtl_per_ha"] = df["yield_qtl_per_ha"].fillna(converted)
        else:
            df["yield_qtl_per_ha"] = converted
        df = df.drop(columns=["yield_kg_per_ha"])
    return df


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["state", "district", "crop"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df


def load_and_clean(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    frames = []
    for path in sorted(raw_dir.glob("*.csv")):
        df = _read_messy_csv(path)
        df = _unify_yield_units(df)
        df = _normalize_text_columns(df)
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"No CSV files found in {raw_dir}")

    combined = pd.concat(frames, ignore_index=True)

    before = len(combined)
    combined = combined.drop_duplicates()
    dropped = before - len(combined)
    if dropped:
        print(f"Dropped {dropped} exact duplicate row(s).")

    missing_yield = combined["yield_qtl_per_ha"].isna().sum()
    if missing_yield:
        print(f"{missing_yield} row(s) have no yield value (kept in output, "
              f"excluded automatically from mean/sum aggregations by pandas).")

    column_order = ["state", "district", "crop", "year", "yield_qtl_per_ha", "area_ha"]
    combined = combined[[c for c in column_order if c in combined.columns]]

    return combined.sort_values(["state", "district", "crop", "year"]).reset_index(drop=True)


def summarize_by_district_crop(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["state", "district", "crop"], as_index=False)
        .agg(
            avg_yield_qtl_per_ha=("yield_qtl_per_ha", "mean"),
            years_covered=("year", "nunique"),
            total_area_ha=("area_ha", "sum"),
        )
        .round({"avg_yield_qtl_per_ha": 2})
    )


def year_over_year_change(df: pd.DataFrame) -> pd.DataFrame:
    y2021 = df[df["year"] == 2021][["state", "district", "crop", "yield_qtl_per_ha"]]
    y2022 = df[df["year"] == 2022][["state", "district", "crop", "yield_qtl_per_ha"]]

    merged = y2021.merge(
        y2022,
        on=["state", "district", "crop"],
        how="outer",
        suffixes=("_2021", "_2022"),
    )
    merged["pct_change"] = (
        (merged["yield_qtl_per_ha_2022"] - merged["yield_qtl_per_ha_2021"])
        / merged["yield_qtl_per_ha_2021"]
        * 100
    ).round(1)

    return merged.sort_values(["state", "district", "crop"]).reset_index(drop=True)


if __name__ == "__main__":
    clean_df = load_and_clean()
    clean_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nWrote {len(clean_df)} cleaned rows to {OUTPUT_PATH}\n")
    print(clean_df.to_string(index=False))

    print("\n--- Average yield by district + crop (groupby) ---")
    print(summarize_by_district_crop(clean_df).to_string(index=False))

    print("\n--- Year-over-year change 2021 -> 2022 (merge) ---")
    print(year_over_year_change(clean_df).to_string(index=False))
