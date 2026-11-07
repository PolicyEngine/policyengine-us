"""Invariants for Alaska's energy relief payment in federal gross income.

Two hold for any payment amount, any year from 2022 on and any state of
residence.

1. A supplied payment raises gross income by the whole payment, wherever the
   recipient lives now, except a payment from the 2022 program, received in
   2022 or 2023, which leaves gross income where it was (IR-2023-23,
   footnote 1; Notice 2023-56, section 4.03). taxable_ak_energy_relief holds
   exactly that change.
2. With no means-tested response in play, the tax on the payment takes less than
   the payment, and household and SPM net income each rise by what remains.

YAML pins the amounts the IRS and Alaska publish for each year, and that the
calculated payment reaches no one outside Alaska. These tests draw amounts,
years and states no published figure names, and they compare two simulations
of one household.
"""

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2022, 2023, 2024, 2025, 2026)
# Recipients got the 2022 program's payments in 2022 or 2023, and the model
# leaves out energy relief from both years (IR-2023-23; Notice 2023-56, section
# 4.03). Alaska paid no energy relief with the 2023 dividend and paid the relief
# the Legislature added in 2023 with the 2024 dividend.
EXCLUDED_YEARS = (2022, 2023)
STATES = ("AK", "HI", "TX", "WA")
# 32-bit floats resolve to $0.03125 at this income, and the net income formulas
# round several times, so a change can differ from its components by a few cents.
TOLERANCE = 0.25
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


@settings(max_examples=10, deadline=None)
@example(state="AK", year=2022, earnings=50_000, payment=662)
@example(state="AK", year=2023, earnings=50_000, payment=662)
@example(state="AK", year=2024, earnings=50_000, payment=298)
@example(state="WA", year=2026, earnings=50_000, payment=200)
@example(state="TX", year=2026, earnings=0, payment=200)
@given(
    state=st.sampled_from(STATES),
    year=st.sampled_from(YEARS),
    earnings=st.integers(min_value=0, max_value=300_000),
    payment=st.integers(min_value=1, max_value=30_000),
)
def test_gross_income_counts_the_payment_wherever_the_recipient_lives(
    state, year, earnings, payment
):
    without = Simulation(situation=one_person(state, year, earnings, 0))
    paid = Simulation(situation=one_person(state, year, earnings, payment))
    expected = 0 if year in EXCLUDED_YEARS else payment
    taxable = calculate(paid, "taxable_ak_energy_relief", year)
    change = calculate(paid, "irs_gross_income", year) - calculate(
        without, "irs_gross_income", year
    )
    assert taxable == pytest.approx(expected, abs=TOLERANCE)
    assert change == pytest.approx(expected, abs=TOLERANCE)


@settings(max_examples=10, deadline=None)
@example(year=2022, payment=662)
@example(year=2023, payment=662)
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
    if year in EXCLUDED_YEARS:
        assert tax == pytest.approx(0, abs=TOLERANCE)
    else:
        assert 0 < tax < payment
    for name in NET_INCOMES:
        change = calculate(paid, name, year) - calculate(without, name, year)
        assert change == pytest.approx(payment - tax, abs=TOLERANCE), name
