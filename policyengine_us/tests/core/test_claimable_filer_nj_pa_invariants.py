"""Check claimable-filer invariants in New Jersey, North Carolina, North Dakota,
Ohio, Oklahoma and Pennsylvania.

Hypothesis draws couples with each adult's claimability, actual claim and
refund-only claimant exception. These tests exchange head and spouse labels
and check that each output stays unchanged. They also mark another filer as
claimed and check that the listed exemptions, credits, deductions and
forgiveness never rise, using generated and seeded populations.

For Pennsylvania, they bound the eligible share between zero and one and
require a full share when neither filer can be claimed. They also check that
forgiveness stays between zero and tax before forgiveness. YAML cases cover
North Dakota's stillborn subtraction; these populations supply no stillborn
children.
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
    money,
)

STATES = ["NJ", "NC", "ND", "OH", "OK", "PA"]
YEARS = [2022, 2025, 2026]
# Amounts that marking another filer as claimed must never raise.
MONOTONE = [
    "nj_dependents_exemption",
    "nj_dependents_attending_college_exemption",
    "nj_ctc",
    "nj_eitc",
    "nc_child_deduction",
    "oh_non_public_school_credits_potential",
    "ok_count_exemptions",
    "ok_stc",
    "ok_eitc",
    "pa_tax_forgiveness_eligible_share",
    "pa_tax_forgiveness_amount",
]
# The Oklahoma child care / child tax credit takes the larger of a care and a
# child tax credit branch; the care branch follows the federal credit, whose
# tax-liability limit can rise when a filer is claimable, so it is checked for
# swap invariance only. Taxes can rise too.
OUTPUTS = MONOTONE + [
    "ok_child_care_child_tax_credit",
    "nj_income_tax",
    "nc_income_tax",
    "nd_income_tax",
    "oh_income_tax",
    "ok_income_tax",
    "pa_income_tax",
]


@st.composite
def children(draw):
    child = draw(dependents())
    return {
        **child,
        "is_full_time_college_student": child["is_full_time_student"],
        "non_public_school_tuition": draw(money(3_000)),
    }


@st.composite
def couples(draw):
    # As in the swap-invariance test: who can be claimed, who of them is
    # actually claimed, and, for the unclaimed, whether the would-be claimant
    # files only for a refund (Publication 501's exception).
    claimable = draw(st.sampled_from(CLAIM_PATTERNS))
    claimed = tuple(can_claim and draw(st.booleans()) for can_claim in claimable)
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(children(), max_size=2)),
        "claimed": claimed,
        "claimable": claimable,
        "exception": tuple(
            not is_claimed and draw(st.booleans()) for is_claimed in claimed
        ),
    }


def _claim_only(units):
    # Monotonicity marks filers as claimed; without separate claimability or
    # exception inputs, claimability follows the claim.
    return [
        {k: v for k, v in unit.items() if k not in ("claimable", "exception")}
        for unit in units
    ]


def _pa_forgiveness_bounds(sim, year):
    share = _calc(sim, "pa_tax_forgiveness_eligible_share", year)
    assert ((share >= 0) & (share <= 1)).all()
    in_pa = np.asarray(sim.calculate("PA", year, map_to="tax_unit"), dtype=bool)
    claimable_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    np.testing.assert_allclose(share[in_pa & ~claimable_filer], 1, atol=0, rtol=0)
    forgiveness = _calc(sim, "pa_tax_forgiveness_amount", year)
    tax = _calc(sim, "pa_income_tax_before_forgiveness", year)
    assert (forgiveness >= 0).all()
    assert (forgiveness <= tax).all()


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_nj_pa_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _pa_forgiveness_bounds)
    check_monotone(_claim_only(units), year, MONOTONE, _pa_forgiveness_bounds)


@pytest.mark.parametrize("year", YEARS)
def test_nj_pa_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=2) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _pa_forgiveness_bounds)
    check_monotone(units, year, MONOTONE, _pa_forgiveness_bounds)
