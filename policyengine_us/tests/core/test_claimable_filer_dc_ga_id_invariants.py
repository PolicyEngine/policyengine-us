"""District of Columbia, Georgia and Idaho rules for a filer who can be claimed
as a dependent.

A return on which the filer, or on a joint return either spouse, can be claimed
as a dependent has no dependents (IRC 152(b)(1)). DC's property tax credit
needs a claimant who was not a dependent or is 65 or older; Georgia's low
income credit and 2023 surplus refund need one filer who qualifies; Idaho's
food tax credit leaves out each filer who can be claimed.

For couples drawn by Hypothesis and a seeded population in these states, with
either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the outputs in
   MONOTONE (amounts not capped by a tax liability that the claim can raise).
3. Identities: a return with a claimable filer has no DC keep child care
   affordable credit or child tax credit and its Idaho food tax credit is at
   most one filer's amount; a return on which every filer can be claimed has
   no Georgia low income credit.

Hypothesis batches check 1 and 3; the seeded population checks 1, 2 and 3.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us.tests.core.test_claimable_filer_federal_invariants import (
    check_monotone,
    check_swap,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    _calc,
    _crafted_cases,
    _seeded_couples,
    adults,
    dependents,
)

STATES = ["DC", "GA", "ID"]
YEARS = [2021, 2023, 2025, 2026]
MONOTONE = [
    "dc_ptc",
    "dc_eitc",
    "dc_kccatc",
    "dc_ctc",
    "ga_exemptions",
    "ga_low_income_credit_potential",
    "ga_ctc_potential",
    "id_grocery_credit",
    "id_household_and_dependent_care_expense_deduction",
]
OUTPUTS = MONOTONE + ["ga_surplus_tax_rebate", "id_2022_rebate"]


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def _identities(sim, year):
    claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    for name in ("dc_kccatc", "dc_ctc"):
        assert not _calc(sim, name, year)[claimed_filer].any(), (
            f"{name} in {year} is positive on a return with a claimable filer"
        )
    # Georgia's low income credit needs one filer who cannot be claimed.
    every_filer = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    assert not _calc(sim, "ga_low_income_credit_potential", year)[every_filer].any()
    # At most the filer who cannot be claimed keeps a food tax credit.
    one_filer = _one_filer_food_amount(sim, year)
    grocery = _calc(sim, "id_grocery_credit", year)
    assert (grocery[claimed_filer] <= one_filer + 0.01).all()


def _one_filer_food_amount(sim, year):
    p = sim.tax_benefit_system.parameters(f"{year}-01-01").gov.states.id.tax.income
    amount = p.credits.grocery.base.amount
    if p.credits.grocery.aged.in_effect:
        amount += p.credits.grocery.aged.amount
    return amount


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_dc_ga_id_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_dc_ga_id_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _identities)
    check_monotone(units, year, MONOTONE, _identities)
