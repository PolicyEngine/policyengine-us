"""Invariants of the official locality sales tax rates.

`policyengine_us/data/local_sales_tax/` stores, for the states with official
locality rate files (New York, Virginia and the Streamlined Sales Tax states
with local sales taxes), the combined state and local general sales tax rate
of each county's places with their own rate and of its area outside them, as
step functions of the date, plus the 2020 Census population of each.
`combined_sales_tax_rate` reads them by county and place FIPS code, and
`local_sales_tax_table` reads the IRS selector's named counties and cities.

Invariants, each tested below:
- L0 official sources only: no sales tax parameter, variable, data file or
  build input names a non-official rate source.
- L1 schema: FIPS formats, one state per county, dates ascending from
  2022-01-01, consecutive rates of a key differ, rates in (0, 0.15).
- L2 coverage: every county of a covered state, in the county FIPS dataset,
  has a rate; the population file has exactly the rate keys; populations are
  non-negative.
- L3 day weighting: the annual rate of every key equals a day-by-day mean of
  its step function, computed independently, for any year, and reproduces the
  worksheet line 3 example (1% for 273 days, 1.75% for 92 days: 1.189%).
- L4 bounds: a key's annual rate lies within its step values; a county's and
  a state's population-weighted rates lie within their keys' rates.
- L5 floors: every covered locality's annual rate is at least its state's
  official general rate, and at least the IRS state table heading rate less
  the IRS rounding, so worksheet line 3 is non-negative from the data, not
  only from its floor at 0.
- L6 lookup precedence: combined_sales_tax_rate returns the place rate, else
  the rate outside places when the place or census block is known, else the
  county's rate, else the state's; a county outside the household's state is
  ignored; a state without official rates gets its heading rate.
- L8 state rates: the official state general rates cover every covered
  state but Nevada, at the statutory rates (New York 4%, Virginia 4.3%,
  Minnesota 6.875%), with South Dakota's cut from 4.5% to 4.2% on 2023-07-01.
- L7 selector lists: each IRS year's (2015-2025) county and place lists are
  disjoint across tables, and name only counties and places in states that
  use the local tables (local_sales_tax_table.yaml tests the precedence
  place > county > state default).
"""

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.simulations import SimulationBuilder

from policyengine_us.model_api import REPO
from policyengine_us.system import system
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    state_fips_by_state_code,
)
from policyengine_us.tools.local_sales_tax_rates import (
    annual_rates,
    locality_populations,
    locality_rate_schedule,
    locality_sales_tax_rates,
    state_general_sales_tax_rates,
    state_rate_schedule,
)

SALT = REPO.joinpath(
    "parameters", "gov", "irs", "deductions", "itemized", "salt_and_real_estate"
)
SELECTOR = SALT / "local_sales_tax_table"
TABLES = ("a", "b", "c", "d")
IRS_YEARS = (2022, 2023, 2024, 2025)
# The IRS table selector has its own lists for each year from 2015; the
# locality rates start in 2022.
SELECTOR_YEARS = tuple(range(2015, 2026))
SCHEDULE = locality_rate_schedule()
COVERED_STATES = sorted(SCHEDULE["state_code"].unique())
KEYS = ["county_fips", "place_fips"]
# New York, Virginia, and the 19 SST member states with local sales taxes.
EXPECTED_STATES = sorted(
    "AR GA IA KS MN NC ND NE NV NY OH OK SD TN UT VA VT WA WI WV WY".split()
)
# IRS headings round state rates to two decimals (Minnesota's 6.875% prints
# as 6.88%), and South Dakota's 2023 heading averages a mid-year change.
HEADING_ROUNDING = 0.0001
SALES_TAX_FILES = [
    *SALT.joinpath("state_sales_tax_table").glob("*.yaml"),
    *SELECTOR.rglob("*.yaml"),
    *REPO.joinpath("variables", "gov", "local", "tax", "sales").glob("*.py"),
    *REPO.joinpath("data", "local_sales_tax").glob("*"),
    REPO / "tools" / "local_sales_tax_rates.py",
    *REPO.parent.joinpath("scripts", "local_sales_tax_rates").glob("*"),
]


def _dated(values, year):
    instant = date(year, 1, 1)
    dates = sorted(d for d in values if d <= instant)
    return values[dates[-1]] if dates else values[min(values)]


def test_l0_official_sources_only():
    """L0: the sales tax files cite no non-official rate source."""
    assert SALES_TAX_FILES
    offenders = [
        str(path)
        for path in SALES_TAX_FILES
        if path.is_file()
        and path.suffix in {".py", ".yaml", ".csv", ".md", ".json"}
        and any(
            name in path.read_text().lower()
            for name in ("taxfoundation", "tax foundation", "average_combined_rate")
        )
    ]
    assert not offenders, offenders
    assert COVERED_STATES == EXPECTED_STATES


def test_l1_schema():
    """L1: every row of the rate and population files."""
    s = SCHEDULE
    assert s["county_fips"].str.fullmatch(r"\d{5}").all()
    assert s["place_fips"].str.fullmatch(r"(\d{5})?").all()
    assert (s.groupby("county_fips")["state_code"].nunique() == 1).all()
    state_fips = state_fips_by_state_code()
    assert (s["county_fips"].str[:2] == s["state_code"].map(state_fips)).all()
    first = s.groupby(KEYS)["effective_from"].transform("min")
    assert (first == pd.Timestamp("2022-01-01")).all()
    assert (s.groupby(KEYS)["effective_from"].diff().dropna() > pd.Timedelta(0)).all()
    previous = s.groupby(KEYS)["rate"].shift()
    assert (previous.isna() | (previous != s["rate"])).all()
    assert ((s["rate"] > 0) & (s["rate"] < 0.15)).all()
    populations = locality_populations()
    assert (populations["population"] >= 0).all()


def test_l2_coverage():
    """L2: every county of every covered state."""
    counties = load_county_fips_dataset()
    covered = set(SCHEDULE["county_fips"])
    for state in COVERED_STATES:
        expected = set(counties.loc[counties["state"] == state, "county_fips"])
        missing = expected - covered
        assert not missing, f"{state}: no rate for {sorted(missing)}"
    rate_keys = set(map(tuple, SCHEDULE[KEYS].drop_duplicates().to_numpy()))
    population_keys = set(map(tuple, locality_populations()[KEYS].to_numpy()))
    assert rate_keys == population_keys


def _daily_mean(rows: pd.DataFrame, year: int) -> float:
    """Day-by-day mean of a key's step function over a calendar year."""
    rows = rows.sort_values("effective_from")
    total, days, day = 0.0, 0, date(year, 1, 1)
    while day.year == year:
        active = rows[rows["effective_from"] <= pd.Timestamp(day)]
        rate = active["rate"].iloc[-1] if len(active) else rows["rate"].iloc[0]
        total += rate
        days += 1
        day += timedelta(days=1)
    return total / days


changing_keys = (
    SCHEDULE[SCHEDULE.duplicated(KEYS, keep=False)][KEYS]
    .drop_duplicates()
    .to_numpy()
    .tolist()
)


@settings(
    max_examples=25,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    keys=st.lists(st.sampled_from(changing_keys), min_size=1, max_size=5),
    year=st.integers(2015, 2030),
)
def test_l3_day_weighting_matches_reference(keys, year):
    """L3: keys whose rate changes, in any year from 2015 to 2030."""
    annual = annual_rates(SCHEDULE, year)
    for county, place in keys:
        rows = SCHEDULE[
            (SCHEDULE["county_fips"] == county) & (SCHEDULE["place_fips"] == place)
        ]
        assert annual[(county, place)] == pytest.approx(
            _daily_mean(rows, year), abs=1e-9
        )


def test_l3_worksheet_line_3_example():
    """L3: "Locality 1 imposed a 1% local general sales tax from January 1
    through September 30, 2025 (273 days). The rate increased to 1.75% for
    the period from October 1 through December 31, 2025 (92 days). You would
    enter "1.189" on line 3" (2025 Instructions for Schedule A)."""
    schedule = pd.DataFrame(
        {
            "county_fips": ["99999", "99999"],
            "place_fips": ["", ""],
            "effective_from": pd.to_datetime(["2022-01-01", "2025-10-01"]),
            "rate": [0.01, 0.0175],
        }
    )
    assert round(annual_rates(schedule, 2025)[("99999", "")] * 100, 3) == 1.189


@pytest.mark.parametrize("year", (2021, 2022, 2025, 2026, 2027))
def test_l4_bounds(year):
    """L4: annual rates within the step values; averages within their keys."""
    annual = annual_rates(SCHEDULE, year)
    bounds = SCHEDULE.groupby(KEYS)["rate"].agg(["min", "max"])
    assert (annual >= bounds["min"] - 1e-12).all()
    assert (annual <= bounds["max"] + 1e-12).all()
    rates = locality_sales_tax_rates(year)
    by_county = annual.groupby(level="county_fips").agg(["min", "max"])
    county = rates.county.reindex(by_county.index)
    assert (county >= by_county["min"] - 1e-12).all()
    assert (county <= by_county["max"] + 1e-12).all()
    for state, value in rates.state.items():
        in_state = rates.county[rates.county_state.reindex(rates.county.index) == state]
        assert in_state.min() - 1e-12 <= value <= in_state.max() + 1e-12


@pytest.mark.parametrize("year", IRS_YEARS + (2026,))
def test_l5_rates_are_at_least_the_heading_rate(year):
    """L5: every key of every covered state."""
    headings = SALT.joinpath("state_sales_tax_table", "rate.yaml")
    with headings.open() as file:
        headings = yaml.safe_load(file)
    annual = annual_rates(SCHEDULE, year).rename("rate").reset_index()
    state = SCHEDULE.drop_duplicates("county_fips").set_index("county_fips")
    annual["state_code"] = annual["county_fips"].map(state["state_code"])
    annual["heading"] = [
        _dated(headings[s], min(year, 2025)) for s in annual["state_code"]
    ]
    below = annual[annual["rate"] < annual["heading"] - HEADING_ROUNDING]
    assert below.empty, below.head().to_dict("records")
    official = annual["state_code"].map(state_general_sales_tax_rates(year))
    below_state = annual[annual["rate"] < official - 1e-12]
    assert below_state.empty, below_state.head().to_dict("records")


def test_l8_state_rates():
    """L8: the official state general sales tax rates."""
    schedule = state_rate_schedule()
    assert set(schedule["state_code"]) == set(COVERED_STATES) - {"NV"}
    first = schedule.groupby("state_code")["effective_from"].min()
    assert (first == pd.Timestamp("2022-01-01")).all()
    assert ((schedule["rate"] > 0.03) & (schedule["rate"] < 0.08)).all()
    rates = state_general_sales_tax_rates(2025)
    assert rates["NY"] == pytest.approx(0.04)
    assert rates["VA"] == pytest.approx(0.043)
    assert rates["MN"] == pytest.approx(0.06875)
    south_dakota = schedule[schedule["state_code"] == "SD"]
    assert list(south_dakota["rate"]) == pytest.approx([0.045, 0.042])
    assert list(south_dakota["effective_from"]) == [
        pd.Timestamp("2022-01-01"),
        pd.Timestamp("2023-07-01"),
    ]
    # 181 days at 4.5% and 184 at 4.2% in 2023.
    assert state_general_sales_tax_rates(2023)["SD"] == pytest.approx(
        (181 * 0.045 + 184 * 0.042) / 365
    )


def _households(year, **inputs):
    n = len(next(iter(inputs.values())))
    simulation = SimulationBuilder().build_default_simulation(system, n)
    for name, values in inputs.items():
        simulation.set_input(name, year, np.array(values))
    return simulation


@pytest.mark.parametrize("year", (2022, 2025, 2026))
def test_l6_lookup_precedence(year):
    """L6: a county with places that have their own rate and an area outside
    them, in each covered state, plus a state without official rates."""
    rates = locality_sales_tax_rates(year)
    first_place = {}
    for key in rates.place.index:
        first_place.setdefault(key[:5], key)
    states, county, place, block, expected = [], [], [], [], []
    for state in COVERED_STATES:
        in_state = [c for c, s in rates.county_state.items() if s == state]
        both = [c for c in in_state if c in first_place and c in rates.outside_places]
        c = both[0] if both else in_state[0]
        cases = [
            (c, "", "", rates.county[c]),  # county only
            ("", "", "", rates.state[state]),  # state only
            ("01001", "", "", rates.state[state]),  # county in another state
        ]
        if both:
            cases += [
                (c, first_place[c][5:], "", rates.place[first_place[c]]),
                (c, "99999", "", rates.outside_places[c]),  # place, no own rate
                (c, "", f"{c}0000001000", rates.outside_places[c]),  # block only
            ]
        for county_fips, place_fips, block_geoid, value in cases:
            states.append(state)
            county.append(county_fips)
            place.append(place_fips)
            block.append(block_geoid)
            expected.append(value)
    # A state without official rates: its heading rate.
    states.append("CA")
    county.append("06037")
    place.append("44000")
    block.append("")
    expected.append(0.0725)
    simulation = _households(
        year,
        state_code=states,
        county_fips=county,
        place_fips=place,
        block_geoid=block,
    )
    actual = simulation.calculate("combined_sales_tax_rate", year)
    np.testing.assert_allclose(actual, expected, rtol=1e-6)


@pytest.mark.parametrize("year", SELECTOR_YEARS)
def test_l7_selector_lists(year):
    """L7: county and place lists of each IRS year."""

    def load(kind, letter):
        with SELECTOR.joinpath(kind, f"{letter}.yaml").open() as file:
            return set(_dated(yaml.safe_load(file)["values"], year) or [])

    with SELECTOR.joinpath("states.yaml").open() as file:
        local_states = set(_dated(yaml.safe_load(file)["values"], year))
    state_fips = state_fips_by_state_code()
    local_fips = {state_fips[s] for s in local_states}
    counties = set(load_county_fips_dataset()["county_fips"])
    for kind in ("county", "place"):
        lists = {letter: load(kind, letter) for letter in TABLES}
        for i, a in enumerate(TABLES):
            for b in TABLES[i + 1 :]:
                assert not lists[a] & lists[b], (kind, a, b)
        for letter, codes in lists.items():
            for code in codes:
                assert code[:2] in local_fips, (kind, letter, code)
                if kind == "county":
                    assert code in counties, code
                else:
                    assert len(code) == 7 and code.isdigit(), code
