"""Rhode Island, South Carolina, Utah, Vermont, West Virginia and Wisconsin
rules for a filer who can be claimed as a dependent.

A return on which the filer (or, if joint, either spouse) can be claimed has
no dependents (IRC 152(b)(1)), so the dependent-based amounts below are zero
on it. Claimant rules (RI property tax relief, VT renter credit, WI homestead
credit) and per-filer exemptions (WV, WI $250) test each spouse separately.

For couples drawn by Hypothesis and a seeded population in these states,
with either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the amounts
   in MONOTONE. The Vermont student loan subtraction, Wisconsin homestead
   income and the West Virginia family credit are left out by design: the
   first replaces the federal deduction a claimed filer loses, and the other
   two rise when a dependent deduction or exemption goes away.
3. Identities: the dependent-based amounts are zero on a return with a
   claimable filer, and a return whose every filer is claimed gets no RI
   property tax relief or VT renter credit and the single $500 West Virginia
   exemption.
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

STATES = ["RI", "SC", "UT", "VT", "WV", "WI"]
YEARS = [2021, 2023, 2025, 2026]
# Zero on a return where either filer can be claimed (IRC 152(b)(1)).
DEPENDENT_BASED = [
    "ri_child_tax_rebate",
    "sc_dependent_exemption",
    "sc_young_child_deduction",
    "ut_total_dependents",
    "ut_personal_exemption",
    "ut_at_home_parent_credit_potential",
    "vt_ctc",
]
MONOTONE = DEPENDENT_BASED + [
    "ri_property_tax_credit",
    "vt_personal_exemptions",
    "vt_renter_credit",
    "wv_personal_exemption",
    "wv_low_income_family_tax_credit_eligible",
    "wv_low_income_family_tax_credit_fpg",
    "wi_standard_deduction",
    "wi_additional_exemption",
    "wi_homestead_credit",
]
OUTPUTS = MONOTONE + [
    "vt_student_loan_interest_subtraction",
    "wv_low_income_family_tax_credit",
    "wi_homestead_income",
    "wi_retirement_income_exclusion_tax",
    "state_income_tax",
]


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def _identities(sim, year):
    either = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    every = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    for name in DEPENDENT_BASED:
        values = _calc(sim, name, year)
        assert not values[either].any(), (
            f"{name} in {year} is positive on a return with a claimable filer"
        )
    for name in ["ri_property_tax_credit", "vt_renter_credit"]:
        assert not _calc(sim, name, year)[every].any(), (
            f"{name} in {year} is positive when every filer is claimed"
        )
    state = np.asarray(sim.calculate("state_code_str", year, map_to="tax_unit"))
    wv_every = every & (state == "WV")
    np.testing.assert_array_equal(
        _calc(sim, "wv_personal_exemption", year)[wv_every], 500
    )


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_ri_sc_ut_vt_wv_wi_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_ri_sc_ut_vt_wv_wi_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=2) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _identities)
    check_monotone(units, year, MONOTONE, _identities)
