"""Invariants of the local general sales tax worksheet (local_sales_tax).

The State and Local General Sales Tax Deduction Worksheet (Instructions for
Schedule A (Form 1040), 2022-2025) sets line 6, the local amount, as:
- 0 for full-year residents of the ten jurisdictions it names after line 1;
- line 2 x line 3 in the states it names on line 2, where line 2 is the
  Optional Local Sales Tax Table amount (for a 1% local rate) and line 3 the
  local rate in percentage points;
- otherwise line 1 x line 3 / line 4, where line 1 is the state table amount
  and line 4 the state rate in the state table heading.
PolicyEngine takes line 3 (local_sales_tax_rate) as the combined state and
local rate minus the state general sales tax rate (the official state rate
where PolicyEngine has the state's rate files, else the heading rate),
floored at 0. The combined rate is the
official locality rate in the states with official rate files, the heading
rate elsewhere, or the rate the user enters.

Invariants, each tested below:
- I1 method partition: each IRS year, the 50 states and DC split exactly into
  the no-local states (table footnote 4), the local-table states (footnote 2,
  plus Alaska), the ratio states (footnote 1, plus California and Nevada), and
  the four states without a state table; the default-table lists partition
  the local-table states.
- I2 non-negativity: local_sales_tax >= 0 for any combined rate.
- I3 no-local zero: local_sales_tax = 0 in the ten no-local jurisdictions.
- I4 threshold: local_sales_tax = 0 whenever the combined rate is at or below
  the state rate b (California at 7.25%, Nevada at 6.85%).
- I5 linearity in line 3: f(b + k x) = k f(b + x), and f never falls as the
  combined rate rises.
- I6 differential: local_sales_tax equals a pure-Python worksheet that reads
  the raw parameter YAML files, over every state, year (2022-2026, 2030),
  family size 1-8, income row, table letter, and several rates.
- I7 local_sales_tax never falls as the income row or family size rises.
- I8 Table D equals the New York state table / 4, rounded half up, in
  2022-2024, and is within 1 of it in 2025 (as printed by the IRS).
- I9 with no rate input, the combined rate is the heading rate and
  local_sales_tax is 0 in every state without official locality rates; in
  the states with them, the combined rate is the state's official
  population-weighted rate, above its state rate.
- I11 entering line 3 directly (local_sales_tax_rate) gives the same amount
  as entering the combined rate it implies.
- I10 local tables after 2025 are the 2025 tables times the IRS uprating
  ratio.

Hypothesis draws the continuous rate and random (state, year, family size,
income row, table) points; each example runs as one vectorized simulation.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from itertools import product

import numpy as np
import pytest
import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.simulations import SimulationBuilder

from policyengine_us.model_api import REPO
from policyengine_us.system import system

STATE_RATES = REPO.joinpath("data", "local_sales_tax", "state_rates.csv")

SALT = REPO.joinpath(
    "parameters", "gov", "irs", "deductions", "itemized", "salt_and_real_estate"
)
IRS_YEARS = (2022, 2023, 2024, 2025)
CHECKED_YEARS = IRS_YEARS + (2026, 2030)
TABLES = ("A", "B", "C", "D")
FAMILY_SIZES = range(1, 9)
INCOME_ROWS = range(1, 20)
STATES = sorted(
    "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
    "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV "
    "WI WY".split()
)
# State table footnotes, 2022-2025. Footnote 4: "This state does not have a
# local general sales tax, so the amount in the state table is the only
# amount to be deducted."
NO_LOCAL = {"CT", "DC", "IN", "KY", "MA", "MD", "ME", "MI", "NJ", "RI"}
# Footnote 2: "Follow the instructions on the next page to determine your
# local sales tax deduction." Worksheet line 2 lists these states and Alaska.
FOOTNOTE_2 = {
    2022: set("AR AZ CO GA IL LA MO MS NC NY SC TN UT VA".split()),
    2023: set("AL AR AZ CO GA IL KS LA MO MS NC NY SC TN UT VA".split()),
}
# Footnote 1: "Use the Ratio Method to determine your local sales tax
# deduction." Footnotes 3 and 5 send California and Nevada residents with a
# larger local tax to the Ratio Method too.
FOOTNOTE_1 = {
    2022: set("AL FL HI IA ID KS MN ND NE NM OH OK PA SD TX VT WA WI WV WY".split()),
    2023: set("FL HI IA ID MN ND NE NM OH OK PA SD TX VT WA WI WV WY".split()),
}
NO_STATE_TABLE = {"DE", "MT", "NH", "OR"}
# States with official locality rate files: New York, Virginia, and the
# Streamlined Sales Tax member states with local sales taxes.
OFFICIAL_RATE_STATES = sorted(
    "AR GA IA KS MN NC ND NE NV NY OH OK SD TN UT VA VT WA WI WV WY".split()
)
TABLE_D_NOTE_EXACT_YEARS = (2022, 2023, 2024)


def _irs_year(year):
    """The IRS table year whose lists apply (2023's lists carry on)."""
    return 2022 if year == 2022 else 2023


def _load(path):
    with path.open() as file:
        return yaml.safe_load(file)


def _dated(values, year):
    """The value in force on January 1 of the year, from a dated mapping."""
    instant = date(year, 1, 1)
    dates = sorted(d for d in values if d <= instant)
    return values[dates[-1]] if dates else values[min(values)]


@pytest.fixture(scope="module")
def raw():
    """The parameter YAML files as written, without the parameter system."""
    return {
        "state_tax": _load(SALT / "state_sales_tax_table" / "tax.yaml"),
        "rate": _load(SALT / "state_sales_tax_table" / "rate.yaml"),
        "no_local": _load(
            SALT / "state_sales_tax_table" / "no_local_sales_tax_states.yaml"
        )["values"],
        "local_tax": _load(SALT / "local_sales_tax_table" / "tax.yaml"),
        "local_states": _load(SALT / "local_sales_tax_table" / "states.yaml")["values"],
        "default": {
            t: _load(
                SALT / "local_sales_tax_table" / "default_table" / f"{t.lower()}.yaml"
            )["values"]
            for t in TABLES
        },
    }


def _uprating_factor(year):
    """Ratio of the IRS uprating index for the year to its 2025 value."""
    uprating = system.parameters.gov.irs.uprating
    if year <= 2025:
        return 1.0
    return uprating(f"{year}-01-01") / uprating("2025-01-01")


class _ReferenceWorksheet:
    """The worksheet's line 6 from the raw YAML files, in plain Python."""

    def __init__(self, raw, year):
        table_year = min(year, 2025)
        factor = _uprating_factor(year)
        self.no_local = set(_dated(raw["no_local"], table_year))
        self.local_states = set(_dated(raw["local_states"], table_year))
        self.heading = {
            s: _dated(raw["rate"][s], table_year) if s in raw["rate"] else 0
            for s in STATES
        }
        official = _official_state_rates(year)
        self.base = {s: official.get(s, self.heading[s]) for s in STATES}
        self.local_table = {
            (t, size, row): _dated(raw["local_tax"][t][size][row], table_year) * factor
            for t, size, row in product(TABLES, range(1, 7), INCOME_ROWS)
        }
        self.state_table = {
            (s, size, row): _dated(raw["state_tax"][s][size][row], table_year) * factor
            for s in STATES
            if s in raw["state_tax"]
            for size, row in product(range(1, 7), INCOME_ROWS)
        }

    def line_6(self, state, size, row, table, combined):
        if state in self.no_local:
            return 0.0
        heading = self.heading[state]
        local_rate = max(combined - self.base[state], 0.0)
        column = min(size, 6)
        if state in self.local_states:
            # Line 2 x line 3, with line 3 in percentage points.
            return self.local_table[(table, column, row)] * local_rate * 100
        if heading == 0:
            return 0.0
        # Line 1 x line 5, where line 5 = line 3 / line 4.
        return self.state_table[(state, column, row)] * local_rate / heading


def _simulate(year, states, sizes, rows, rates, tables=None):
    """One single-person household per point; returns local_sales_tax."""
    simulation = SimulationBuilder().build_default_simulation(system, len(states))
    simulation.set_input("state_code", year, np.array(states))
    simulation.set_input("tax_unit_size", year, np.array(sizes))
    simulation.set_input("state_sales_tax_income_bracket", year, np.array(rows))
    simulation.set_input("combined_sales_tax_rate", year, np.array(rates))
    if tables is not None:
        simulation.set_input("local_sales_tax_table", year, np.array(tables))
    return simulation.calculate("local_sales_tax", year)


def _heading_rates(year):
    rates = system.parameters.gov.irs.deductions.itemized.salt_and_real_estate
    rates = rates.state_sales_tax_table.rate(f"{year}-01-01")
    return {state: float(rates[state]) for state in STATES}


def _official_state_rates(year):
    """Day-by-day mean over the year of each state's rate in the official
    state rate file, read directly; each state's first rate also covers the
    days before its first row."""
    rows = {}
    with STATE_RATES.open() as file:
        next(file)
        for line in file:
            state, start, rate = line.strip().split(",")
            rows.setdefault(state, []).append((date.fromisoformat(start), float(rate)))
    means = {}
    for state, steps in rows.items():
        steps.sort()
        day, total, days = date(year, 1, 1), 0.0, 0
        while day.year == year:
            in_force = [r for start, r in steps if start <= day] or [steps[0][1]]
            total += in_force[-1]
            days += 1
            day = date.fromordinal(day.toordinal() + 1)
        means[state] = total / days
    return means


def _state_rates(year):
    """Line 3's base: the official state rate where the state's files give
    it, else the heading rate."""
    official = _official_state_rates(year)
    headings = _heading_rates(year)
    return {s: official.get(s, headings[s]) for s in STATES}


# Hypothesis strategies: a batch of worksheet points in one year.
points = st.lists(
    st.tuples(
        st.sampled_from(STATES),
        st.sampled_from(FAMILY_SIZES),
        st.sampled_from(INCOME_ROWS),
        st.sampled_from(TABLES),
    ),
    min_size=1,
    max_size=60,
)
years = st.sampled_from(CHECKED_YEARS)
# A fixed seed and no example database keep CI runs reproducible and leave no
# files behind; the grid tests below cover the finite dimensions exhaustively.
HYPOTHESIS_SETTINGS = settings(
    max_examples=25,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[
        HealthCheck.too_slow,
        HealthCheck.data_too_large,
        HealthCheck.large_base_example,
    ],
)


@pytest.mark.parametrize("year", IRS_YEARS)
def test_i1_methods_partition_the_jurisdictions(raw, year):
    """I1: every state and DC gets exactly one worksheet method."""
    irs_year = _irs_year(year)
    no_local = set(_dated(raw["no_local"], year))
    local_table = set(_dated(raw["local_states"], year))
    rates = {s: _dated(raw["rate"][s], year) for s in raw["rate"] if len(s) == 2}
    ratio = {
        s for s in STATES if rates.get(s, 0) > 0 and s not in no_local | local_table
    }
    no_table = {s for s in STATES if rates.get(s, 0) == 0} - local_table
    assert no_local == NO_LOCAL
    assert local_table == FOOTNOTE_2[irs_year] | {"AK"}
    assert ratio == FOOTNOTE_1[irs_year] | {"CA", "NV"}
    assert no_table == NO_STATE_TABLE
    groups = [no_local, local_table, ratio, no_table]
    assert sum(len(g) for g in groups) == len(STATES) == 51
    assert set().union(*groups) == set(STATES)
    # The default tables cover each local-table state exactly once.
    defaults = [set(_dated(raw["default"][t], year)) for t in TABLES]
    assert sum(len(d) for d in defaults) == len(local_table)
    assert set().union(*defaults) == local_table


@HYPOTHESIS_SETTINGS
@given(year=years, batch=points, data=st.data())
def test_i2_local_sales_tax_is_never_negative(year, batch, data):
    """I2: any combined rate from 0 to 20%, including below the heading."""
    rates = data.draw(
        st.lists(
            st.floats(0, 0.2, allow_nan=False),
            min_size=len(batch),
            max_size=len(batch),
        )
    )
    states, sizes, rows, tables = zip(*batch)
    amounts = _simulate(year, states, sizes, rows, rates, tables)
    assert (amounts >= 0).all()


@HYPOTHESIS_SETTINGS
@given(year=years, batch=points, rate=st.floats(0, 0.2, allow_nan=False))
def test_i3_no_local_jurisdictions_are_zero(year, batch, rate):
    """I3: the ten no-local jurisdictions at any rate, size, row, and table."""
    no_local = sorted(NO_LOCAL)
    states = [no_local[i % len(no_local)] for i in range(len(batch))]
    _, sizes, rows, tables = zip(*batch)
    amounts = _simulate(year, states, sizes, rows, [rate] * len(batch), tables)
    assert (amounts == 0).all()


@HYPOTHESIS_SETTINGS
@given(
    year=years,
    batch=points,
    shares=st.lists(st.floats(0, 1), min_size=60, max_size=60),
)
def test_i4_zero_at_or_below_the_heading_rate(year, batch, shares):
    """I4: combined rate = state rate x a share in [0, 1]."""
    bases = _state_rates(year)
    states, sizes, rows, tables = zip(*batch)
    rates = [bases[s] * shares[i] for i, s in enumerate(states)]
    amounts = _simulate(year, states, sizes, rows, rates, tables)
    assert (amounts == 0).all()


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_i4_california_and_nevada_no_box(year):
    """I4: California at 7.25% and Nevada at 6.85% enter no local rate."""
    amounts = _simulate(year, ["CA", "NV"], [2, 2], [8, 8], [0.0725, 0.0685])
    assert list(amounts) == [0, 0]
    above = _simulate(year, ["CA", "NV"], [2, 2], [8, 8], [0.0726, 0.0686])
    assert (above > 0).all()


@HYPOTHESIS_SETTINGS
@given(
    year=years,
    batch=points,
    x=st.floats(0.001, 0.05),
    k=st.floats(0.5, 4),
)
def test_i5_linear_and_monotone_in_the_local_rate(year, batch, x, k):
    """I5: f(b + k x) = k f(b + x), and f(b + x) <= f(b + k x) when k >= 1."""
    bases = _state_rates(year)
    states, sizes, rows, tables = zip(*batch)
    base = [bases[s] + x for s in states]
    scaled = [bases[s] + k * x for s in states]
    f_base = _simulate(year, states, sizes, rows, base, tables)
    f_scaled = _simulate(year, states, sizes, rows, scaled, tables)
    np.testing.assert_allclose(f_scaled, k * f_base, rtol=1e-4, atol=0.01)
    low, high = (f_base, f_scaled) if k >= 1 else (f_scaled, f_base)
    assert (low <= high).all()


RATES = (0.0, 0.04, 0.0725, 0.0912, 0.115)


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_i6_matches_a_reference_worksheet(raw, year):
    """I6: every state, family size 1-8, income row, table, and five rates
    (0%, 4%, 7.25%, 9.12%, 11.5%)."""
    grid = list(product(STATES, FAMILY_SIZES, INCOME_ROWS, TABLES, RATES))
    states, sizes, rows, tables, rates = zip(*grid)
    actual = _simulate(year, states, sizes, rows, rates, tables)
    reference = _ReferenceWorksheet(raw, year)
    expected = [reference.line_6(*point) for point in grid]
    np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-3)


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_i7_never_falls_as_income_row_or_family_size_rises(year):
    """I7: every state and table, family size 1-8, income row, at 9.5%."""
    grid = list(product(STATES, TABLES, FAMILY_SIZES, INCOME_ROWS))
    states, tables, sizes, rows = zip(*grid)
    amounts = _simulate(year, states, sizes, rows, [0.095] * len(grid), tables)
    amounts = amounts.reshape(
        len(STATES), len(TABLES), len(FAMILY_SIZES), len(INCOME_ROWS)
    )
    assert (np.diff(amounts, axis=2) >= 0).all(), "falls as family size rises"
    assert (np.diff(amounts, axis=3) >= 0).all(), "falls as the income row rises"


@pytest.mark.parametrize("year", IRS_YEARS)
def test_i8_table_d_is_a_quarter_of_the_new_york_table(raw, year):
    """I8: selector note "* Note: Local Table D is just 25% of the NY State
    table." Exact after half-up rounding in 2022-2024; the printed 2025 Table D
    departs from it by up to 1 in some cells."""
    instant = date(year, 1, 1)
    gaps = []
    for size, row in product(range(1, 7), INCOME_ROWS):
        new_york = raw["state_tax"]["NY"][size][row][instant]
        table_d = raw["local_tax"]["D"][size][row][instant]
        quarter = Decimal(new_york) / 4
        rounded = int(quarter.quantize(Decimal(1), rounding=ROUND_HALF_UP))
        gaps.append((table_d - rounded, abs(Decimal(table_d) - quarter)))
    if year in TABLE_D_NOTE_EXACT_YEARS:
        assert all(gap == 0 for gap, _ in gaps)
    else:
        assert all(distance <= 1 for _, distance in gaps)


@pytest.mark.parametrize("year", CHECKED_YEARS + (2021,))
def test_i9_no_rate_input(year):
    """I9: every state and DC, every family size and income row, with no rate
    input and no county."""
    grid = list(product(STATES, FAMILY_SIZES, INCOME_ROWS))
    states, sizes, rows = zip(*grid)
    simulation = SimulationBuilder().build_default_simulation(system, len(grid))
    simulation.set_input("state_code", year, np.array(states))
    simulation.set_input("tax_unit_size", year, np.array(sizes))
    simulation.set_input("state_sales_tax_income_bracket", year, np.array(rows))
    combined = simulation.calculate("combined_sales_tax_rate", year)
    amounts = simulation.calculate("local_sales_tax", year)
    headings = _heading_rates(year)
    heading = np.array([headings[s] for s in states], dtype=np.float32)
    bases = _state_rates(year)
    base = np.array([bases[s] for s in states], dtype=np.float32)
    official = np.isin(states, OFFICIAL_RATE_STATES)
    assert (combined[~official] == heading[~official]).all()
    assert (amounts[~official] == 0).all()
    assert (combined[official] > base[official]).all()
    assert (amounts[official] > 0).all()


@HYPOTHESIS_SETTINGS
@given(year=years, batch=points, x=st.floats(0, 0.05, allow_nan=False))
def test_i11_local_rate_input_matches_combined_rate_input(year, batch, x):
    """I11: line 3 entered directly, or implied by a combined rate."""
    bases = _state_rates(year)
    states, sizes, rows, tables = zip(*batch)
    by_combined = _simulate(
        year, states, sizes, rows, [bases[s] + x for s in states], tables
    )
    simulation = SimulationBuilder().build_default_simulation(system, len(batch))
    simulation.set_input("state_code", year, np.array(states))
    simulation.set_input("tax_unit_size", year, np.array(sizes))
    simulation.set_input("state_sales_tax_income_bracket", year, np.array(rows))
    simulation.set_input("local_sales_tax_rate", year, np.full(len(batch), x))
    simulation.set_input("local_sales_tax_table", year, np.array(tables))
    by_local = simulation.calculate("local_sales_tax", year)
    np.testing.assert_allclose(by_local, by_combined, rtol=1e-4, atol=0.01)


@pytest.mark.parametrize("year", (2026, 2030))
def test_i10_local_tables_uprate_from_2025(year):
    """I10: every table, family size, and income row."""
    tables = system.parameters.gov.irs.deductions.itemized.salt_and_real_estate
    tables = tables.local_sales_tax_table.tax
    later = tables(f"{year}-01-01")
    last = tables("2025-01-01")
    factor = _uprating_factor(year)
    assert factor > 1
    for table, size, row in product(TABLES, range(1, 7), INCOME_ROWS):
        assert later[table][str(size)][str(row)] == pytest.approx(
            last[table][str(size)][str(row)] * factor, rel=1e-9
        )
