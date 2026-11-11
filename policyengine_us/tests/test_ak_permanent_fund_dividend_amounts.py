"""Invariants for the amounts Alaska paid with each Permanent Fund Dividend.

1. For each dividend year from 2015 to 2026, the dividend plus energy relief
   equals the whole payment per eligible individual that Alaska published. The
   PFD Division publishes 2015 to 2025 in its summary table, and the Department
   of Revenue published 2026 in release 26-004. PolicyEngine rounds 2022's
   $2,621.81 and $662.19 to $2,622 and $662, which keeps the $3,284 total.
2. From 2015 to 2100, the dividend stays positive and energy relief never
   falls below zero.
3. Alaska has set neither amount for 2027 or later, so from 2027 the dividend
   stays at the 2026 amount and energy relief at zero.

The YAML tests pin each year's dividend and energy relief one at a time. These
tests compare the two parameters' sum with the published whole payment, and
draw years beyond the published ones.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

# "Dividend Amount" in the PFD Division's Summary of Dividend Applications &
# Payments, https://pfd.alaska.gov/division-info/summary-of-dividend-applications-payments
# (2015 to 2025), and the $1,000 dividend with the $200 energy relief payment in
# Department of Revenue release 26-004 (2026).
WHOLE_PAYMENT = {
    2015: 2_072,
    2016: 1_022,
    2017: 1_100,
    2018: 1_600,
    2019: 1_606,
    2020: 992,
    2021: 1_114,
    2022: 3_284,
    2023: 1_312,
    2024: 1_702,
    2025: 1_000,
    2026: 1_200,
}
LAST_SET_YEAR = max(WHOLE_PAYMENT)


def amounts(year):
    # Read the two parameters at the instant, not the whole tree, which would
    # build every parameter for each year drawn.
    dor = system.parameters.gov.states.ak.dor
    instant = f"{year}-01-01"
    return (
        float(dor.permanent_fund_dividend(instant)),
        float(dor.energy_relief(instant)),
    )


def test_published_years_start_at_first_modeled_year():
    assert min(WHOLE_PAYMENT) == FIRST_MODELED_YEAR


@pytest.mark.parametrize("year", sorted(WHOLE_PAYMENT))
def test_dividend_and_energy_relief_add_up_to_the_published_payment(year):
    dividend, energy_relief = amounts(year)
    assert dividend + energy_relief == pytest.approx(WHOLE_PAYMENT[year], abs=0.005)


@given(st.integers(min_value=FIRST_MODELED_YEAR, max_value=2100))
def test_amounts_stay_in_bounds(year):
    dividend, energy_relief = amounts(year)
    assert dividend > 0
    assert energy_relief >= 0


@given(st.integers(min_value=LAST_SET_YEAR + 1, max_value=2100))
def test_later_years_carry_the_last_dividend_and_no_energy_relief(year):
    assert amounts(year) == (amounts(LAST_SET_YEAR)[0], 0)
