import pandas as pd
from pathlib import Path

FOLDER = Path(__file__).parent

TERRITORY_PSEUDO_COUNTY_FIPS = {
    "AS": ("60010", "60020", "60030", "60040", "60050"),
    "MP": ("69085", "69100", "69110", "69120"),
}


def _county_fips_from_hud_area_code(hud_area_codes: pd.Series) -> pd.Series:
    """Extract the county FIPS prefix from HUD FMR area codes.

    HUD county-level FMR files include five-digit county FIPS for some areas
    and FMR-area codes such as 600199999 for others. The latter encode the
    county in the first five digits after zero-padding to ten characters.
    """
    codes = hud_area_codes.astype(str).str.strip()
    direct_county = codes.str.len() == 5
    derived_county = codes.str.zfill(10).str[:5]
    return codes.where(direct_county, derived_county).str.zfill(5)


def _expand_territory_pseudo_counties(raw: pd.DataFrame) -> pd.DataFrame:
    frames = [
        raw[
            ~raw["state"].isin(TERRITORY_PSEUDO_COUNTY_FIPS)
            | raw["county_fips"].isin(
                {
                    county_fips
                    for county_fips_list in TERRITORY_PSEUDO_COUNTY_FIPS.values()
                    for county_fips in county_fips_list
                }
            )
        ]
    ]

    for state, county_fips_list in TERRITORY_PSEUDO_COUNTY_FIPS.items():
        pseudo_rows = raw[
            (raw["state"] == state) & ~raw["county_fips"].isin(county_fips_list)
        ]
        for county_fips in county_fips_list:
            county_rows = pseudo_rows.copy()
            county_rows["county_fips"] = county_fips
            county_rows["is_direct_county_fips"] = False
            frames.append(county_rows)

    return pd.concat(frames, ignore_index=True)


def _load_raw_fair_market_rents() -> pd.DataFrame:
    raw = pd.read_csv(
        FOLDER / "fair_market_rents.csv",
        dtype={"hud_fmr_area_code": str},
    )
    raw["hud_fmr_area_code"] = raw["hud_fmr_area_code"].str.strip()
    raw["county_fips"] = _county_fips_from_hud_area_code(raw["hud_fmr_area_code"])
    raw["is_direct_county_fips"] = raw["hud_fmr_area_code"].str.len() == 5
    return _expand_territory_pseudo_counties(raw)


def _to_county_level_fair_market_rents(raw: pd.DataFrame) -> pd.DataFrame:
    index = ["county_fips", "year", "bedrooms"]
    direct_county_rows = raw[raw["is_direct_county_fips"]]
    derived_county_rows = raw[~raw["is_direct_county_fips"]]

    # When county alone is less granular than HUD's FMR area code, use the
    # median area value as a lossy county-level fallback. A direct five-digit
    # county row, when present, is HUD's county-level value and overrides it.
    county_fallback = derived_county_rows.groupby(index, as_index=False)[
        "value"
    ].median()
    direct_county = direct_county_rows[index + ["value"]]
    return (
        pd.concat([county_fallback, direct_county], ignore_index=True)
        .drop_duplicates(index, keep="last")
        .sort_values(index)
        .reset_index(drop=True)
    )


raw_fair_market_rents = _load_raw_fair_market_rents()
fair_market_rents = _to_county_level_fair_market_rents(raw_fair_market_rents)
available_fmr_years = sorted(fair_market_rents["year"].unique().tolist())


def nearest_fmr_year(year: int) -> int:
    prior_years = [candidate for candidate in available_fmr_years if candidate <= year]
    if prior_years:
        return max(prior_years)
    return min(available_fmr_years)


def _load_small_area_fair_market_rents() -> pd.DataFrame:
    """ZIP-level Small Area FMRs, indexed by (zip_code, year, bedrooms).

    Scoped to the four Texas metros where HUD mandates SAFMR use under the
    Housing Choice Voucher program: Dallas, Fort Worth-Arlington, and San
    Antonio (2018 cohort) plus Beaumont-Port Arthur (2024 cohort). Houston is
    not a designated metro. Outside these areas the model keeps the county FMR.
    """
    raw = pd.read_csv(
        FOLDER / "small_area_fair_market_rents.csv",
        dtype={"zip_code": str},
    )
    raw["zip_code"] = raw["zip_code"].str.strip().str.zfill(5)
    return raw


small_area_fair_market_rents = _load_small_area_fair_market_rents()
available_safmr_years = sorted(small_area_fair_market_rents["year"].unique().tolist())


def nearest_safmr_year(year: int) -> int:
    prior_years = [
        candidate for candidate in available_safmr_years if candidate <= year
    ]
    if prior_years:
        return max(prior_years)
    return min(available_safmr_years)
