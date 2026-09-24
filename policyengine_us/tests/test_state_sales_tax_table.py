"""Structural checks on the IRS Optional State Sales Tax Table (#9595).

The IRS prints the table in blocks of three states, six family-size columns
each. A three-column shift within those blocks once left 30 jurisdictions
with another state's values in some or all family-size columns, which put
some family-size-6 amounts below family-size-1 amounts. The IRS amounts never
fall as family size or income rises, so a monotonicity check catches that
kind of transcription error.
"""

from datetime import date

import pytest
import yaml
from policyengine_core.parameters import get_parameter

from policyengine_us import CountryTaxBenefitSystem
from policyengine_us.model_api import REPO

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


@pytest.fixture(scope="module")
def table_yaml():
    with (TABLE_DIR / "tax.yaml").open() as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="module")
def table_parameter():
    return get_parameter(CountryTaxBenefitSystem().parameters, f"{TABLE_PATH}.tax")


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
