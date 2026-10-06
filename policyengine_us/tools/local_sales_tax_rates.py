"""Official combined state and local general sales tax rates by locality.

`policyengine_us/data/local_sales_tax/rates.csv` holds, for each county in
the states with official locality rate files (New York, Virginia and the
Streamlined Sales Tax member states with local sales taxes), the combined
rate of each of its places with its own rate (`place_fips`) and of its area
outside them (`place_fips` empty), as a step function of the date: a row
applies from `effective_from` until the key's next row, and a key's last row
applies indefinitely. Every key's first row is dated 2022-01-01 and also
applies to earlier years. `populations.csv` holds each key's 2020 Census
population, and `state_rates.csv` the state general sales tax rate of each
covered state (except Nevada, whose files fold its state rate into county
rates), in the same step form. The files are built by
`scripts/local_sales_tax_rates/build.py` from the sources listed in
`SOURCES.md` beside them.

`locality_sales_tax_rates(year)` returns each key's rate for a tax year,
averaged over the days of the year as the sales tax deduction worksheet's
line 3 instructions direct when a rate changes during the year: "Multiply
each tax rate for the period it was in effect by a fraction. The numerator
of the fraction is the number of days the rate was in effect ... and the
denominator is the total number of days in the year."
"""

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

import pandas as pd

DATA_PACKAGE = "policyengine_us.data"
DATA_FOLDER = "local_sales_tax"


def _read(name: str) -> pd.DataFrame:
    path = resources.files(DATA_PACKAGE).joinpath(DATA_FOLDER, name)
    with path.open("rb") as f:
        return pd.read_csv(
            f,
            dtype={"county_fips": str, "place_fips": str, "state_code": str},
            keep_default_na=False,
        )


@lru_cache(maxsize=None)
def locality_rate_schedule() -> pd.DataFrame:
    df = _read("rates.csv")
    df["effective_from"] = pd.to_datetime(df["effective_from"])
    return df.sort_values(["county_fips", "place_fips", "effective_from"]).reset_index(
        drop=True
    )


@lru_cache(maxsize=None)
def locality_populations() -> pd.DataFrame:
    return _read("populations.csv")


@lru_cache(maxsize=None)
def state_rate_schedule() -> pd.DataFrame:
    df = _read("state_rates.csv")
    df["effective_from"] = pd.to_datetime(df["effective_from"])
    df["county_fips"] = df["state_code"]
    df["place_fips"] = ""
    return df.sort_values(["state_code", "effective_from"]).reset_index(drop=True)


@lru_cache(maxsize=None)
def state_general_sales_tax_rates(year: int) -> pd.Series:
    """Day-weighted state general sales tax rate of each covered state over
    the year, indexed by state code."""
    annual = annual_rates(state_rate_schedule(), year)
    return pd.Series(annual.to_numpy(), index=annual.index.get_level_values(0))


def annual_rates(schedule: pd.DataFrame, year: int) -> pd.Series:
    """Day-weighted average rate over calendar `year` of each key of
    `schedule`, indexed by (county_fips, place_fips). A key's first rate also
    covers the days before its first row."""
    start_of_year = pd.Timestamp(year=year, month=1, day=1)
    end_of_year = pd.Timestamp(year=year, month=12, day=31)
    days_in_year = (end_of_year - start_of_year).days + 1
    keys = ["county_fips", "place_fips"]
    next_start = schedule.groupby(keys)["effective_from"].shift(-1)
    is_first = ~schedule.duplicated(keys)
    start = schedule["effective_from"].where(~is_first, pd.Timestamp.min)
    start = start.clip(lower=start_of_year)
    end = (next_start - pd.Timedelta(days=1)).fillna(end_of_year)
    end = end.clip(upper=end_of_year)
    days = ((end - start).dt.days + 1).clip(lower=0)
    weighted = schedule["rate"] * days / days_in_year
    return weighted.groupby([schedule[k] for k in keys]).sum()


@dataclass(frozen=True)
class LocalitySalesTaxRates:
    """Annual combined sales tax rates of the covered localities.

    - `place`: rate of each place with its own rate, indexed by county FIPS
      code and place code (10 characters).
    - `outside_places`: rate of each county's area outside those places,
      indexed by county FIPS code.
    - `county`: population-weighted rate of each county, indexed by county
      FIPS code.
    - `state`: population-weighted rate of each covered state, indexed by
      state code.
    - `county_state`: state code of each covered county.
    """

    place: pd.Series
    outside_places: pd.Series
    county: pd.Series
    state: pd.Series
    county_state: pd.Series


@lru_cache(maxsize=None)
def locality_sales_tax_rates(year: int) -> LocalitySalesTaxRates:
    """Annual locality rates for a tax year."""
    schedule = locality_rate_schedule()
    rates = annual_rates(schedule, year).rename("rate").reset_index()
    rates = rates.merge(
        locality_populations(),
        on=["county_fips", "place_fips"],
        how="left",
        validate="one_to_one",
    )
    county_state = schedule.drop_duplicates("county_fips").set_index("county_fips")[
        "state_code"
    ]
    rates["state_code"] = rates["county_fips"].map(county_state)
    is_outside = rates["place_fips"] == ""
    places = rates[~is_outside]
    outside = rates[is_outside].set_index("county_fips")["rate"]
    weighted = rates["rate"] * rates["population"]
    county = (
        weighted.groupby(rates["county_fips"]).sum()
        / rates.groupby("county_fips")["population"].sum()
    )
    state = (
        weighted.groupby(rates["state_code"]).sum()
        / rates.groupby("state_code")["population"].sum()
    )
    return LocalitySalesTaxRates(
        place=pd.Series(
            places["rate"].to_numpy(),
            index=places["county_fips"] + places["place_fips"],
        ),
        outside_places=outside,
        county=county,
        state=state,
        county_state=county_state,
    )
