"""Invariants for Alaska's energy relief payment in federal gross income.

Three hold for any payment amount and any year from 2022 on.

1. Gross income rises by the whole payment, except in 2022, when it does not
   move (IR-2023-23, footnote 1).
2. taxable_ak_energy_relief stays between zero and the payment, and it stays at
   zero outside Alaska.
3. With no means-tested response in play, the tax on the payment takes less than
   the payment, and household and SPM net income each rise by what remains.

YAML pins the amounts the IRS and Alaska publish for each year. These tests need
Hypothesis over amounts no published figure names, and they compare two
simulations of one household.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2022, 2023, 2024, 2025, 2026)
EXCLUDED_YEAR = 2022
TOLERANCE = 0.02
# Earnings this high rule out every means-tested response.
HIGH_EARNINGS = 500_000
NET_INCOMES = ("household_net_income", "spm_unit_net_income")


def one_person(state, year, earnings, payment):
    members = ["you"]
    return {
        "people": {
            "you": {
                "age": {year: 40},
                "employment_income": {year: earnings},
                "ak_energy_relief": {year: payment},
            }
        },
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, "state_name": {year: state}}},
    }


def calculate(simulation, name, year):
    return float(simulation.calculate(name, year).sum())


@settings(max_examples=20, deadline=None)
@example(year=2022, earnings=50_000, payment=662)
@example(year=2024, earnings=50_000, payment=298)
@example(year=2026, earnings=0, payment=200)
@given(
    year=st.sampled_from(YEARS),
    earnings=st.integers(min_value=0, max_value=300_000),
    payment=st.integers(min_value=1, max_value=30_000),
)
def test_gross_income_rises_by_the_payment_except_in_2022(year, earnings, payment):
    without = Simulation(situation=one_person("AK", year, earnings, 0))
    paid = Simulation(situation=one_person("AK", year, earnings, payment))
    change = calculate(paid, "irs_gross_income", year) - calculate(
        without, "irs_gross_income", year
    )
    expected = 0 if year == EXCLUDED_YEAR else payment
    assert change == pytest.approx(expected, abs=TOLERANCE)


@settings(max_examples=20, deadline=None)
@example(state="WA", year=2026, payment=200)
@example(state="AK", year=2022, payment=662)
@given(
    state=st.sampled_from(("AK", "HI", "TX", "WA")),
    year=st.sampled_from(YEARS),
    payment=st.integers(min_value=0, max_value=30_000),
)
def test_taxable_amount_stays_within_the_payment_and_in_alaska(state, year, payment):
    simulation = Simulation(situation=one_person(state, year, 50_000, payment))
    taxable = calculate(simulation, "taxable_ak_energy_relief", year)
    assert 0 <= taxable <= payment
    if state != "AK":
        assert taxable == 0


@settings(max_examples=20, deadline=None)
@example(year=2022, payment=662)
@example(year=2024, payment=298)
@example(year=2026, payment=200)
@given(
    year=st.sampled_from(YEARS),
    payment=st.integers(min_value=1, max_value=30_000),
)
def test_net_incomes_rise_by_the_payment_less_its_tax(year, payment):
    without = Simulation(situation=one_person("AK", year, HIGH_EARNINGS, 0))
    paid = Simulation(situation=one_person("AK", year, HIGH_EARNINGS, payment))
    tax = calculate(paid, "income_tax", year) - calculate(without, "income_tax", year)
    if year == EXCLUDED_YEAR:
        assert tax == pytest.approx(0, abs=TOLERANCE)
    else:
        assert 0 < tax < payment
    for name in NET_INCOMES:
        change = calculate(paid, name, year) - calculate(without, name, year)
        assert change == pytest.approx(payment - tax, abs=TOLERANCE), name
