from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

FOLDER = Path(__file__).parent

income_limits = pd.read_csv(
    FOLDER / "section8_income_limits.csv",
    dtype={"county_fips": str},
)
available_income_limit_years = sorted(income_limits["year"].unique().tolist())


@lru_cache
def _income_limits_for_year(year: int) -> pd.DataFrame:
    prior = income_limits[income_limits["year"] <= year]
    candidates = (
        prior
        if len(prior)
        else income_limits[income_limits["year"] == min(available_income_limit_years)]
    )
    return (
        candidates.sort_values(["county_fips", "year"])
        .drop_duplicates("county_fips", keep="last")
        .reset_index(drop=True)
    )


def _county_fips_series(county_fips: np.ndarray) -> pd.Series:
    return pd.Series(np.asarray(county_fips).astype(str)).str.zfill(5)


def lookup_income_limit(
    county_fips: np.ndarray,
    year: int,
    column: str,
) -> np.ndarray:
    df = pd.DataFrame({"county_fips": _county_fips_series(county_fips)})
    rows = _income_limits_for_year(year)[["county_fips", column]]
    matched = df.merge(rows, on="county_fips", how="left")
    return matched[column].fillna(0).to_numpy()


def lookup_sized_income_limit(
    county_fips: np.ndarray,
    family_size: np.ndarray,
    year: int,
    prefix: str,
) -> np.ndarray:
    columns = [f"{prefix}_{size}" for size in range(1, 9)]
    df = pd.DataFrame({"county_fips": _county_fips_series(county_fips)})
    rows = _income_limits_for_year(year)[["county_fips", *columns]]
    matched = df.merge(rows, on="county_fips", how="left")
    values = matched[columns].fillna(0).to_numpy()
    lookup_size = np.clip(np.asarray(family_size).astype(int), 1, 8)
    return values[np.arange(len(values)), lookup_size - 1]
