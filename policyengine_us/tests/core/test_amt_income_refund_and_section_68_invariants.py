"""Alternative minimum taxable income leaves out tax refunds and section 68.

26 U.S.C. 56(b)(1)(C): no recovery of state or local taxes is in alternative
minimum taxable income (Form 6251 line 2b). 56(b)(1)(E): section 68 does not
apply. With the itemization choice fixed and no deductions that depend on AGI
(no medical expenses, charity well under its AGI limits), adding a state tax
refund to a filer's income must leave AMTI unchanged in every year: the refund
enters AGI and is subtracted back, and any change it causes in the section 68
reduction or the capped SALT deduction cancels because AMTI reverses the
first and adds back the second.

Each Hypothesis example evaluates a batch of tax units and their twins
without the refund in one vectorized simulation, in a state with no income tax.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01


@st.composite
def tax_unit(draw):
    earnings = draw(st.integers(20_000, 3_000_000))
    return {
        "joint": draw(st.booleans()),
        "itemizes": draw(st.booleans()),
        "employment_income": earnings,
        "salt_refund_income": draw(st.integers(1, 20_000)),
        "real_estate_taxes": draw(st.integers(0, 40_000)),
        "home_mortgage_interest": draw(st.integers(0, 40_000)),
        # Under 10% of earnings keeps charity below every AGI limit.
        "charitable_cash_donations": draw(st.integers(0, earnings // 10)),
    }


def _amt_income(units, year):
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for twin in (0, 1):
        for i, unit in enumerate(units):
            head = f"head_{twin}_{i}"
            members = [head]
            situation["people"][head] = {
                "age": {year: 45},
                "employment_income": {year: unit["employment_income"]},
                "salt_refund_income": {
                    year: unit["salt_refund_income"] if twin == 0 else 0
                },
                "real_estate_taxes": {year: unit["real_estate_taxes"]},
                "home_mortgage_interest": {year: unit["home_mortgage_interest"]},
                "charitable_cash_donations": {year: unit["charitable_cash_donations"]},
            }
            if unit["joint"]:
                spouse = f"spouse_{twin}_{i}"
                situation["people"][spouse] = {"age": {year: 45}}
                members.append(spouse)
            situation["tax_units"][f"unit_{twin}_{i}"] = {
                "members": members,
                "tax_unit_itemizes": {year: unit["itemizes"]},
            }
            situation["households"][f"household_{twin}_{i}"] = {
                "members": members,
                "state_code": {year: "TX"},
            }
    simulation = Simulation(situation=situation)
    amti = np.asarray(simulation.calculate("amt_income", year), dtype=float)
    return amti[: len(units)], amti[len(units) :]


@pytest.mark.parametrize("year", [2017, 2025, 2026])
@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(units=st.lists(tax_unit(), min_size=8, max_size=8))
def test_state_tax_refund_does_not_change_amt_income(year, units):
    with_refund, without_refund = _amt_income(units, year)
    np.testing.assert_allclose(with_refund, without_refund, atol=TOLERANCE)
