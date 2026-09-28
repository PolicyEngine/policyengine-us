"""Structural checks on the IRS Optional State Sales Tax Table (#9595).

The IRS prints the table in blocks of three states, six family-size columns
each. A three-column shift within those blocks once left 30 jurisdictions
with another state's values in some or all family-size columns. Two checks
catch that kind of transcription error:

- The IRS amounts never fall as family size or income rises. The shift put
  some family-size-6 amounts below family-size-1 amounts.
- No two family-size columns of the IRS table are identical. The shift copied
  whole columns from one state to another, which a monotonicity check misses
  when the copied state's own row happens to rise.

The variable-level tests run grids of single-person households through the
formulas that read the table:

- state_sales_tax returns the table cell for every state, family size 1 to 8
  (capped at the "Over 5" column), and income row, in each IRS table year.
- The income row is the IRS row whose "At least" floor the income has reached,
  on both sides of every row boundary, and every income source counts toward
  it.
- state_sales_tax never falls as adjusted gross income or family size rises.
- local_sales_tax is zero in the ten jurisdictions whose residents the
  worksheet sends to -0- on line 6, and 20% of state_sales_tax elsewhere.
- state_and_local_sales_or_income_tax is the larger of the income tax (state
  withholding plus local income tax) and the sales tax (state plus local).

Each test's docstring gives its grid and the inputs it holds fixed.
"""

from bisect import bisect_right
from datetime import date
from itertools import product

import numpy as np
import pytest
import yaml
from policyengine_core.parameters import get_parameter
from policyengine_core.simulations import SimulationBuilder

from policyengine_us.model_api import REPO
from policyengine_us.system import system

TABLE_PATH = "gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table"
TABLE_DIR = REPO.joinpath("parameters", *TABLE_PATH.split("."))
IRS_TABLE_YEARS = (2022, 2023, 2024, 2025)
# Later years are uprated from the last IRS table.
CHECKED_YEARS = IRS_TABLE_YEARS + (2026, 2030)
FAMILY_SIZES = range(1, 7)
INCOME_BRACKETS = range(1, 20)
# The IRS table covers the 45 states with a state general sales tax and DC.
# Alaska has no state sales tax and is kept at zero.
IRS_JURISDICTIONS = {
    "AL", "AZ", "AR", "CA", "CO", "CT", "DC", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "NE", "NV", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
}  # fmt: skip
# Worksheet, instruction after line 1: "If, for all of 2023, you lived only in
# Connecticut, the District of Columbia, Indiana, Kentucky, Maine, Maryland,
# Massachusetts, Michigan, New Jersey, or Rhode Island, skip lines 2 through 5,
# enter -0- on line 6" (same list in 2022, 2024, and 2025).
NO_LOCAL_SALES_TAX = ["CT", "DC", "IN", "KY", "MA", "MD", "ME", "MI", "NJ", "RI"]
# Lower bound of each IRS income row after the first ("At least").
IRS_ROW_FLOORS = [
    20_000, 30_000, 40_000, 50_000, 60_000, 70_000, 80_000, 90_000, 100_000,
    120_000, 140_000, 160_000, 180_000, 200_000, 225_000, 250_000, 275_000,
    300_000,
]  # fmt: skip
# Family sizes above 6 use the "Over 5" column.
SIMULATED_FAMILY_SIZES = range(1, 9)
# The IRS counts income as "the amount shown on your Form 1040 or 1040-SR,
# line 11 [line 11b in 2025], plus any nontaxable items, such as" tax-exempt
# interest, veterans' benefits, workers' compensation, the nontaxable part of
# social security and of IRA, pension, or annuity distributions, and public
# assistance payments. These are the PolicyEngine variables for those items.
TABLE_INCOME_SOURCES = [
    "adjusted_gross_income",
    "tax_exempt_interest_income",
    "veterans_benefits",
    "workers_compensation",
    "tax_exempt_social_security",
    "tax_exempt_pension_income",
    "tax_exempt_retirement_distributions",
    "tanf",
    "ssi",
]


@pytest.fixture(scope="module")
def table_yaml():
    with (TABLE_DIR / "tax.yaml").open() as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="module")
def table_parameter():
    return get_parameter(system.parameters, f"{TABLE_PATH}.tax")


def _states(table_yaml):
    return {key for key in table_yaml if key not in ("description", "metadata")}


def test_table_covers_the_irs_jurisdictions_and_alaska(table_yaml):
    assert _states(table_yaml) == IRS_JURISDICTIONS | {"AK"}


def test_every_cell_has_a_value_for_each_irs_table_year(table_yaml):
    expected_dates = {date(year, 1, 1) for year in IRS_TABLE_YEARS}
    missing = []
    for state in sorted(_states(table_yaml)):
        assert set(table_yaml[state]) == set(FAMILY_SIZES), state
        for size in FAMILY_SIZES:
            assert set(table_yaml[state][size]) == set(INCOME_BRACKETS), (
                state,
                size,
            )
            for bracket in INCOME_BRACKETS:
                dates = set(table_yaml[state][size][bracket])
                if not expected_dates <= dates:
                    missing.append((state, size, bracket))
    assert not missing, f"Cells missing an IRS table year: {missing[:10]}"


def test_alaska_is_zero(table_yaml):
    values = {
        value
        for size in FAMILY_SIZES
        for bracket in INCOME_BRACKETS
        for value in table_yaml["AK"][size][bracket].values()
    }
    assert values == {0}


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_table_is_non_decreasing_in_family_size_and_income(table_parameter, year):
    table = table_parameter(f"{year}-01-01")
    violations = []
    for state in sorted(IRS_JURISDICTIONS | {"AK"}):
        cells = [
            [table[state][str(size)][str(bracket)] for size in FAMILY_SIZES]
            for bracket in INCOME_BRACKETS
        ]
        for row, amounts in enumerate(cells):
            for column, amount in enumerate(amounts):
                if column and amount < amounts[column - 1]:
                    violations.append(
                        f"{state} bracket {row + 1}: family size "
                        f"{column + 1} ({amount}) < size {column} "
                        f"({amounts[column - 1]})"
                    )
                if row and amount < cells[row - 1][column]:
                    violations.append(
                        f"{state} family size {column + 1}: bracket "
                        f"{row + 1} ({amount}) < bracket {row} "
                        f"({cells[row - 1][column]})"
                    )
    assert not violations, "\n".join(violations[:20])


@pytest.mark.parametrize("year", IRS_TABLE_YEARS)
def test_no_family_size_column_repeats_another(table_yaml, year):
    columns = {}
    for state in sorted(IRS_JURISDICTIONS):
        for size in FAMILY_SIZES:
            column = tuple(
                table_yaml[state][size][bracket][date(year, 1, 1)]
                for bracket in INCOME_BRACKETS
            )
            columns.setdefault(column, []).append(f"{state} family size {size}")
    repeats = [cells for cells in columns.values() if len(cells) > 1]
    assert not repeats, f"Identical columns: {repeats[:10]}"


def _grid_simulation(year, states, sizes, **inputs):
    """One single-person household per grid point, with the given inputs."""
    simulation = SimulationBuilder().build_default_simulation(system, len(states))
    simulation.set_input("state_code", year, np.array(states))
    simulation.set_input("tax_unit_size", year, np.array(sizes))
    for name, values in inputs.items():
        if system.variables[name].definition_period == "month":
            for month in range(1, 13):
                simulation.set_input(name, f"{year}-{month:02d}", np.array(values) / 12)
        else:
            simulation.set_input(name, year, np.array(values))
    return simulation


def _income_inputs(**amounts):
    """Every table income source, zero unless given."""
    size = len(next(iter(amounts.values())))
    return {name: amounts.get(name, np.zeros(size)) for name in TABLE_INCOME_SOURCES}


@pytest.mark.parametrize("year", IRS_TABLE_YEARS)
def test_state_sales_tax_returns_the_table_cell(table_yaml, year):
    """Every state, family size 1 to 8, and income row (7,144 points)."""
    grid = list(
        product(
            sorted(IRS_JURISDICTIONS | {"AK"}),
            SIMULATED_FAMILY_SIZES,
            INCOME_BRACKETS,
        )
    )
    states, sizes, brackets = zip(*grid)
    simulation = _grid_simulation(
        year, states, sizes, state_sales_tax_income_bracket=brackets
    )
    expected = [
        table_yaml[state][min(size, 6)][bracket][date(year, 1, 1)]
        for state, size, bracket in grid
    ]
    actual = simulation.calculate("state_sales_tax", year)
    assert np.array_equal(actual, expected)


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_state_sales_tax_never_falls_as_income_or_family_size_rises(year):
    """Every state and family size 1 to 8, at $0, $1 million, and both sides of
    every income row floor; income is adjusted gross income only."""
    incomes = sorted({0, 1_000_000} | {f + d for f in IRS_ROW_FLOORS for d in (-1, 0)})
    states = sorted(IRS_JURISDICTIONS | {"AK"})
    grid = list(product(states, SIMULATED_FAMILY_SIZES, incomes))
    grid_states, sizes, grid_incomes = zip(*grid)
    simulation = _grid_simulation(
        year,
        grid_states,
        sizes,
        **_income_inputs(adjusted_gross_income=np.array(grid_incomes)),
    )
    brackets = simulation.calculate("state_sales_tax_income_bracket", year)
    expected_brackets = [
        bisect_right(IRS_ROW_FLOORS, income) + 1 for income in grid_incomes
    ]
    assert np.array_equal(brackets, expected_brackets)
    amounts = simulation.calculate("state_sales_tax", year).reshape(
        len(states), len(SIMULATED_FAMILY_SIZES), len(incomes)
    )
    assert (np.diff(amounts, axis=1) >= 0).all(), "falls as family size rises"
    assert (np.diff(amounts, axis=2) >= 0).all(), "falls as income rises"


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_every_income_source_counts_toward_the_income_row(year):
    """$25,000 from one source at a time, and from none; the rest are zero."""
    sources = TABLE_INCOME_SOURCES
    count = len(sources) + 1
    amounts = {
        name: np.array([25_000 if row == column else 0 for row in range(count)])
        for column, name in enumerate(sources)
    }
    simulation = _grid_simulation(
        year, ["TX"] * count, [1] * count, **_income_inputs(**amounts)
    )
    brackets = simulation.calculate("state_sales_tax_income_bracket", year)
    # $25,000 is in the $20,000-$30,000 row; no income is in the first row.
    assert list(brackets) == [2] * len(sources) + [1], dict(
        zip(sources + ["none"], brackets)
    )


@pytest.mark.parametrize("year", CHECKED_YEARS)
def test_local_sales_tax_is_zero_or_twenty_percent_of_state_amount(year):
    """Every state, family size 1 to 8, and income row."""
    grid = list(
        product(
            sorted(IRS_JURISDICTIONS | {"AK"}),
            SIMULATED_FAMILY_SIZES,
            INCOME_BRACKETS,
        )
    )
    states, sizes, brackets = zip(*grid)
    simulation = _grid_simulation(
        year, states, sizes, state_sales_tax_income_bracket=brackets
    )
    state_amount = simulation.calculate("state_sales_tax", year)
    local_amount = simulation.calculate("local_sales_tax", year)
    no_local = np.isin(states, NO_LOCAL_SALES_TAX)
    assert (local_amount[no_local] == 0).all()
    assert np.allclose(local_amount[~no_local], 0.2 * state_amount[~no_local])


@pytest.mark.parametrize("year", IRS_TABLE_YEARS)
def test_sales_or_income_tax_is_the_larger_amount(year):
    """Every state at family sizes 1, 4, and 8 and income rows 1, 10, and 19,
    crossed with state withholding of $0-$5,000 and local income tax of $0 or
    $300."""
    grid = list(
        product(
            sorted(IRS_JURISDICTIONS | {"AK"}),
            (1, 4, 8),
            (1, 10, 19),
            (0, 400, 900, 5_000),
            (0, 300),
        )
    )
    states, sizes, brackets, withheld, local_income = zip(*grid)
    simulation = _grid_simulation(
        year,
        states,
        sizes,
        state_sales_tax_income_bracket=brackets,
        state_withheld_income_tax=withheld,
        local_income_tax=local_income,
    )
    income_tax = np.add(withheld, local_income)
    sales_tax = simulation.calculate("state_sales_tax", year) + simulation.calculate(
        "local_sales_tax", year
    )
    actual = simulation.calculate("state_and_local_sales_or_income_tax", year)
    assert np.allclose(actual, np.maximum(income_tax, sales_tax))
