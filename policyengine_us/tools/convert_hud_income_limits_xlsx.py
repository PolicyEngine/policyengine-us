"""Convert HUD's Section 8 Income Limits workbook into the PolicyEngine CSV.

HUD publishes one Section 8 Income Limits workbook per fiscal year on
huduser.gov (browse to ``Datasets > Income Limits`` and download
``Section8-FYXX.xlsx``; the static files live under ``il/ilXX/`` — e.g.
``il/il26/Section8-FY26.xlsx`` for FY2026 — not ``il2026/``, which is the
interactive query tool). The sheet holds one row per HUD income-limit area
(some subcounty), with a 10-digit ``fips`` whose first five digits are the
county FIPS, the area median income, and family-size columns for each limit
tier.

huduser.gov serves the static files only to requests with a browser
``User-Agent``; a bare download gets a bot challenge (HTTP 202, zero bytes).

Dependency: ``python-calamine`` (``pip install python-calamine``). HUD's
workbooks ship with malformed metadata timestamps that openpyxl rejects;
calamine reads them cleanly. Not a runtime dependency of the model — only
needed when refreshing the bundled CSV.

Usage:
    python -m policyengine_us.tools.convert_hud_income_limits_xlsx \
        --input ~/Downloads/Section8-FY26.xlsx \
        --year 2026 \
        --output \
        policyengine_us/parameters/gov/hud/income_limits/section8_income_limits.csv

HUD publishes ``ELI_``/``l50_``/``l80_`` (30/50/80 percent AMI) verbatim —
they already reflect HUD's hold-harmless, high-cost, and national caps plus
the federal-poverty-guideline floor on ELI — so this script copies them
directly rather than recomputing from the median. Subcounty rows are
collapsed to the county median, matching the FMR / income-limit README
pattern, and the script merges into the existing CSV (de-duplicates on
``(county_fips, year)``) so re-running across multiple year files appends
rather than overwrites.
"""

import argparse
from pathlib import Path

import pandas as pd

# HUD Section 8 workbook column -> PolicyEngine tier prefix. ``medianYEAR`` is
# handled separately because the suffix is the fiscal year.
TIER_SOURCE_PREFIX = {
    "extremely_low_income": "ELI",  # 30% AMI
    "very_low_income": "l50",  # 50% AMI
    "low_income": "l80",  # 80% AMI
}
FAMILY_SIZES = range(1, 9)
SIZED_COLUMNS = [
    f"{tier}_{size}" for tier in TIER_SOURCE_PREFIX for size in FAMILY_SIZES
]
NUMERIC_COLUMNS = ["ami", *SIZED_COLUMNS]


def read_sheet(path: Path) -> pd.DataFrame:
    """Load the Section 8 sheet (the one carrying a ``fips`` column).

    Uses the ``calamine`` engine because HUD's published workbooks ship with
    malformed timestamps in their metadata that openpyxl rejects.
    """
    workbook = pd.ExcelFile(path, engine="calamine")
    for sheet in workbook.sheet_names:
        df = workbook.parse(sheet)
        if "fips" in df.columns:
            return df
    raise ValueError(f"No sheet in {path} contains a 'fips' column.")


def reshape(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Map HUD columns to the PolicyEngine schema and collapse to county median."""
    median_col = f"median{year}"
    source_sized = [
        f"{source_prefix}_{size}"
        for source_prefix in TIER_SOURCE_PREFIX.values()
        for size in FAMILY_SIZES
    ]
    required = ["fips", median_col, *source_sized]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(
            f"Workbook missing expected columns {missing}. "
            f"Columns present: {list(df.columns)}"
        )

    out = pd.DataFrame(
        {
            "county_fips": df["fips"].astype("int64").astype(str).str.zfill(10).str[:5],
            "ami": df[median_col],
        }
    )
    for tier, source_prefix in TIER_SOURCE_PREFIX.items():
        for size in FAMILY_SIZES:
            out[f"{tier}_{size}"] = df[f"{source_prefix}_{size}"]

    # Collapse subcounty (HMFA) rows to the county median. HUD's published
    # limits are whole dollars, and the medians land on whole dollars too;
    # store integers to match the existing CSV.
    collapsed = out.groupby("county_fips", as_index=False)[NUMERIC_COLUMNS].median()
    collapsed[NUMERIC_COLUMNS] = collapsed[NUMERIC_COLUMNS].round().astype("int64")
    collapsed["year"] = year
    return collapsed[["county_fips", "year", *NUMERIC_COLUMNS]]


def merge_with_existing(new: pd.DataFrame, output: Path) -> pd.DataFrame:
    if not output.exists():
        combined = new
    else:
        existing = pd.read_csv(output, dtype={"county_fips": str})
        existing["county_fips"] = existing["county_fips"].str.zfill(5)
        combined = pd.concat([existing, new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["county_fips", "year"], keep="last")
    # Sort by (county_fips, year) so each county's fiscal years stay adjacent,
    # matching the bundled file; appending a new year is then pure insertions.
    return combined.sort_values(["county_fips", "year"]).reset_index(drop=True)


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
    combined.to_csv(args.output, index=False, lineterminator="\n")
    print(f"Wrote {len(combined):,} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
