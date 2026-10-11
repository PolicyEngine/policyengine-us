"""New Jersey, North Carolina, North Dakota, Ohio, Oklahoma and Pennsylvania
rules for a filer who can be claimed as a dependent.

A return on which the filer (or, if joint, either spouse) can be claimed as a
dependent has no dependents (IRC 152(b)(1)), so the NJ dependent, college
and child tax credit counts, Ohio's tuition credit, Oklahoma's dependent
exemptions and sales tax credit dependents, North Dakota's stillborn
subtraction and Pennsylvania's dependent child allowance count none. A
claimable filer has no Oklahoma regular exemption, no childless NJ or
Oklahoma EITC, and claims Pennsylvania Tax Forgiveness only on their own tax
and only when the parent who claims them qualifies.

For couples drawn by Hypothesis (with claimability, the actual claim and the
refund-only claimant exception drawn per adult) and a seeded population in
these states, each output is the same under either head/spouse labelling, and
marking another filer as claimed never raises the exemptions, credits,
deductions and forgiveness changed here.
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us.tests.core.test_claimable_filer_federal_invariants import (
    check_monotone,
    check_swap,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
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
def filers(draw):
    # Whether the parent who claims this adult qualifies for Pennsylvania
    # Tax Forgiveness (read only when the adult can be claimed).
    return {
        **draw(adults()),
        "pa_tax_forgiveness_parent_qualifies": draw(st.booleans()),
    }


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
        "adults": [draw(filers()), draw(filers())],
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


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_nj_pa_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS)
    check_monotone(_claim_only(units), year, MONOTONE)


@pytest.mark.parametrize("year", YEARS)
def test_nj_pa_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=2) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, MONOTONE)
