"""Convert HUD's FY-XX FMR Excel workbook into the PolicyEngine CSV schema.

HUD publishes one Excel file per fiscal year on huduser.gov (browse to
``Datasets > Fair Market Rents`` and download ``FYXX_FMRs.xlsx``). The
sheet structure is stable year to year: one row per FMR area, with
columns for each bedroom count and a 5-digit county FIPS.

Dependency: ``python-calamine`` (``pip install python-calamine``). HUD's
workbooks ship with malformed metadata timestamps that openpyxl rejects;
calamine reads them cleanly. Not a runtime dependency of the model — only
needed when refreshing the bundled CSV.

Usage:
    python -m policyengine_us.tools.convert_hud_fmr_xlsx \
        --input ~/Downloads/FY25_FMRs.xlsx \
        --year 2025 \
        --output policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv

The script merges into the existing CSV (de-duplicates on
``(state, county_fips, year, bedrooms)``) so re-running across multiple
year files appends rather than overwrites.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# HUD's column naming has drifted slightly over the years. The script
# tolerates the common variants for each field.
STATE_COLS = ("stusps", "state_alpha", "state_code")
COUNTY_COLS = ("fips", "fips2020", "fips2010", "fips_county", "cntycode")
BEDROOM_COLS = {
    0: ("fmr_0", "fmr0", "FMR_0BR", "Efficiency"),
    1: ("fmr_1", "fmr1", "FMR_1BR", "One-Bedroom"),
    2: ("fmr_2", "fmr2", "FMR_2BR", "Two-Bedroom"),
    3: ("fmr_3", "fmr3", "FMR_3BR", "Three-Bedroom"),
    4: ("fmr_4", "fmr4", "FMR_4BR", "Four-Bedroom"),
}


def pick(df: pd.DataFrame, candidates: tuple[str, ...], required: bool = True) -> str:
    for name in candidates:
        if name in df.columns:
            return name
    if required:
        raise KeyError(
            f"None of {candidates} present. Workbook columns: {list(df.columns)}"
        )
    return ""


def read_sheet(path: Path) -> pd.DataFrame:
    """Load the first sheet that contains an FMR column.

    Uses the ``calamine`` engine because HUD's published workbooks ship with
    malformed timestamps in their metadata that openpyxl rejects.
    """
    workbook = pd.ExcelFile(path, engine="calamine")
    for sheet in workbook.sheet_names:
        df = workbook.parse(sheet)
        df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]
        if any(
            any(col == c for col in df.columns)
            for variants in BEDROOM_COLS.values()
            for c in variants
        ):
            return df
    raise ValueError(f"No sheet in {path} contains an fmr_0..fmr_4 column.")


def reshape(df: pd.DataFrame, year: int) -> pd.DataFrame:
    state_col = pick(df, STATE_COLS)
    county_col = pick(df, COUNTY_COLS)
    rows = []
    for bedrooms, candidates in BEDROOM_COLS.items():
        col = pick(df, tuple(c.lower() for c in candidates), required=False)
        if not col:
            print(f"  bedrooms={bedrooms}: no column found, skipping", file=sys.stderr)
            continue
        slice_ = df[[state_col, county_col, col]].dropna()
        slice_ = slice_.rename(
            columns={
                state_col: "state",
                county_col: "hud_fmr_area_code",
                col: "value",
            }
        )
        slice_["bedrooms"] = bedrooms
        slice_["year"] = year
        rows.append(slice_)
    out = pd.concat(rows, ignore_index=True)
    out["hud_fmr_area_code"] = (
        out["hud_fmr_area_code"].astype(int).astype(str).str.zfill(5)
    )
    out["value"] = out["value"].astype(float)
    return out[["state", "hud_fmr_area_code", "year", "bedrooms", "value"]].sort_values(
        ["state", "hud_fmr_area_code", "year", "bedrooms"]
    )


def merge_with_existing(new: pd.DataFrame, output: Path) -> pd.DataFrame:
    if not output.exists():
        return new
    existing = pd.read_csv(output, dtype={"hud_fmr_area_code": str})
    existing["hud_fmr_area_code"] = existing["hud_fmr_area_code"].str.zfill(5)
    combined = pd.concat([existing, new], ignore_index=True)
    return combined.drop_duplicates(
        subset=["state", "hud_fmr_area_code", "year", "bedrooms"], keep="last"
    ).sort_values(["state", "hud_fmr_area_code", "year", "bedrooms"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = read_sheet(args.input)
    new = reshape(raw, args.year)
    combined = merge_with_existing(new, args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False)
    print(f"Wrote {len(combined):,} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
