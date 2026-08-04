"""County-level HUD utility allowance schedules.

Utility allowances are set per public housing agency (PHA) under 24 CFR 982.517,
by dwelling-unit size (bedroom count) and utility/fuel type. There is no national
dataset of these schedules, so this file encodes the schedules for the specific
counties PolicyEngine currently models (LA County, the TDHCA service area in
Texas, and four Kansas PHAs).

Each schedule is collapsed into a single monthly dollar amount per bedroom size
using one consistent convention, matching how LA County was originally modeled:

    Multi-Family (apartment) unit type
      + all-electric heating / cooking / water heating
      + sum of every tenant-paid line item
        (other electric, air conditioning, water, sewer, trash, the electric
         service charge, and the range and refrigerator appliance allowances)

Gas rows, gas service charges, and electric heat-pump rows are excluded.

`county_utility_allowances.csv` stores the raw per-county schedules keyed by
`county_fips`, `year` (the schedule's effective year), and `bedrooms` (with
`-1` denoting single-room occupancy). `utility_allowance_schedule(year)` returns
the effective schedule for a given year, expanded to bedrooms 0-8. Counties
whose PHA publishes no SRO row fall back to their zero-bedroom value flagged
with `sro_uses_zero_bedroom_share`; the SRO share of the zero-bedroom allowance
(75% per 24 CFR 982.604(b)) is a reform-visible parameter applied post-lookup
in the `hud_utility_allowance` formula.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

FOLDER = Path(__file__).parent

# Household bedroom counts are clipped to this range before lookup; schedules
# that stop at a smaller size reuse their largest published bedroom value.
MAX_BEDROOMS = 8
# Sentinel bedroom key for single-room-occupancy (SRO) units.
SRO_BEDROOMS = -1


def _load_county_utility_allowances() -> pd.DataFrame:
    df = pd.read_csv(
        FOLDER / "county_utility_allowances.csv",
        dtype={"county_fips": str},
    )
    df["county_fips"] = df["county_fips"].str.zfill(5)
    return df


county_utility_allowances = _load_county_utility_allowances()


def _effective_year_by_county(target_year: int) -> pd.Series:
    """Latest schedule year at or before `target_year` for each county, falling
    back to the county's earliest schedule year for years before it begins."""
    df = county_utility_allowances
    prior = df[df["year"] <= target_year].groupby("county_fips")["year"].max()
    earliest = df.groupby("county_fips")["year"].min()
    return prior.reindex(earliest.index).fillna(earliest).astype(int)


@lru_cache(maxsize=None)
def utility_allowance_schedule(target_year: int) -> pd.DataFrame:
    """Effective monthly utility allowance per county and bedroom size for a
    year, expanded to bedrooms 0-`MAX_BEDROOMS` (plus SRO).

    The returned frame carries a `sro_uses_zero_bedroom_share` flag: it is True
    only for the SRO row of a county whose PHA publishes no dedicated SRO row,
    where `monthly_value` holds the (unscaled) zero-bedroom allowance. The
    `hud_utility_allowance` formula scales those rows by the SRO share parameter
    (75% per 24 CFR 982.604(b)); published SRO rows pass through unscaled."""
    df = county_utility_allowances
    effective = _effective_year_by_county(target_year)
    selected = df[
        df.apply(lambda row: row["year"] == effective[row["county_fips"]], axis=1)
    ]

    rows = []
    for county_fips, group in selected.groupby("county_fips"):
        by_bedroom = dict(zip(group["bedrooms"], group["monthly_value"]))
        largest = max(bedroom for bedroom in by_bedroom if bedroom >= 0)
        for bedrooms in range(MAX_BEDROOMS + 1):
            value = by_bedroom.get(bedrooms, by_bedroom[largest])
            rows.append((county_fips, bedrooms, value, False))
        if SRO_BEDROOMS in by_bedroom:
            # Published SRO row: use it directly, no share scaling.
            rows.append((county_fips, SRO_BEDROOMS, by_bedroom[SRO_BEDROOMS], False))
        else:
            # No published SRO row: hold the zero-bedroom value and flag it for
            # the SRO-share scaling applied in the formula.
            rows.append((county_fips, SRO_BEDROOMS, by_bedroom[0], True))

    return pd.DataFrame(
        rows,
        columns=[
            "county_fips",
            "bedrooms",
            "monthly_value",
            "sro_uses_zero_bedroom_share",
        ],
    )
