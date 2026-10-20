"""Colorado, Connecticut, Illinois and Indiana rules for a filer who can be
claimed as a dependent.

A return on which the filer, or on a joint return either spouse, can be claimed
as a dependent without the filing exception has no dependents (IRC 152(b)(1)),
so it gets no state dependent exemption or child-based deduction, and a
childless filer who can be claimed gets no state EITC through the ITIN or age
extensions (IRC 32(c)(1)(A)(ii)(III)). Colorado's child credit before 2024 also
requires allowable dependents; from 2024 its child and family credits follow
IRC 152(c) qualifying-child status. Indiana keeps each filer's own $1,000
exemption; Illinois' child tax credit follows the IRC 152 qualifying child.

For couples drawn by Hypothesis and a seeded population in these states, with
either, both or neither spouse claimed, claimability drawn separately from
actual claims, and the filing exception:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the outputs in
   MONOTONE (amounts not capped by a tax liability that the claim can raise).
3. Identities: when
   `head_or_spouse_is_dependent_elsewhere_without_filing_exception` is true,
   the return has no Illinois dependent exemption or Indiana additional
   exemption, and its Indiana base exemptions are $1,000 per filer. Colorado's
   child tax credit is also zero before 2024; from 2024 qualifying children
   remain eligible. Otherwise Illinois and Indiana also count the dependents.
   Illinois rebate eligibility follows actual claims, even when both spouses
   are claimable.

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

STATES = ["CO", "CT", "IL", "IN"]
YEARS = [2021, 2023, 2025, 2026]
MONOTONE = [
    "co_eitc",
    "co_ctc",
    "co_low_income_cdcc",
    "ct_property_tax_credit_eligible",
    "ct_child_tax_rebate",
    "il_dependent_exemption",
    "il_eitc",
    "il_ctc",
    "il_income_tax_rebate",
    "il_income_tax_rebate_eligible",
    "in_base_exemptions",
    "in_additional_exemptions",
    "in_adoption_exemption",
]
OUTPUTS = MONOTONE + ["co_refundable_credits"]


@st.composite
def couples(draw):
    claimable = draw(st.sampled_from(CLAIM_PATTERNS))
    claimed = tuple(can_claim and draw(st.booleans()) for can_claim in claimable)
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": claimed,
        "claimable": claimable,
        "exception": tuple(
            not is_claimed and draw(st.booleans()) for is_claimed in claimed
        ),
    }


def _claimability_cases():
    # Distinguish claimability from actual claims, and guarantee exception
    # coverage without relying on Hypothesis to draw a child in IL or IN.
    return [
        {
            "state": state,
            "adults": [{"age": 26, "employment_income": 1_000}, {"age": 30}],
            "dependents": [{"age": 5}],
            "claimed": claimed,
            "claimable": (True, True),
            "exception": exception,
        }
        for state in STATES
        for claimed, exception in (
            ((False, False), (False, False)),
            ((False, False), (True, True)),
            ((True, True), (False, False)),
        )
    ]


def _identities(units):
    states = np.array([unit["state"] for unit in units])

    def check(sim, year):
        blocked_filer = (
            _calc(
                sim,
                "head_or_spouse_is_dependent_elsewhere_without_filing_exception",
                year,
            )
            > 0
        )
        # Each unit is simulated as consecutive copies (labellings or claim
        # patterns), in the order of the units.
        state = np.repeat(states, len(blocked_filer) // len(units))
        dependent_outputs = (
            "il_dependent_exemption",
            "in_additional_exemptions",
        )
        if year < 2024:
            dependent_outputs += ("co_ctc",)
        for name in dependent_outputs:
            assert not _calc(sim, name, year)[blocked_filer].any(), (
                f"{name} in {year} is positive on a return with a claimable "
                "filer without the filing exception"
            )
        dependents_count = _calc(sim, "tax_unit_dependents", year)
        allowed_dependents = np.where(blocked_filer, 0, dependents_count)
        p = sim.tax_benefit_system.parameters(year).gov.states
        mask = state == "IL"
        np.testing.assert_array_equal(
            _calc(sim, "il_dependent_exemption", year)[mask],
            p.il.tax.income.exemption.dependent * allowed_dependents[mask],
            err_msg="Illinois must restore dependents under the filing exception",
        )
        filers = _calc(sim, "tax_unit_size", year) - dependents_count
        mask = state == "IN"
        np.testing.assert_array_equal(
            _calc(sim, "in_base_exemptions", year)[mask],
            p["in"].tax.income.exemptions.base.amount
            * (filers + allowed_dependents)[mask],
            err_msg="Indiana must restore dependents under the filing exception",
        )
        # All generated joint returns have AGI below $400,000. Section
        # 212.1(a) excludes actual claims, rather than claimability, and keeps
        # the joint return eligible while either spouse is not claimed.
        person_is_filer = _calc(sim, "is_tax_unit_head_or_spouse", year) > 0
        actually_claimed = (
            _calc(sim, "claimed_as_dependent_on_another_return", year) > 0
        )
        eligible_filers = sim.populations["tax_unit"].sum(
            person_is_filer & ~actually_claimed
        )
        mask = state == "IL"
        np.testing.assert_array_equal(
            _calc(sim, "il_income_tax_rebate_eligible", year)[mask],
            eligible_filers[mask] > 0,
            err_msg="Illinois rebate eligibility must follow actual claims",
        )

    return check


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_co_ct_il_in_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities(units))


@pytest.mark.parametrize("year", YEARS)
def test_co_ct_il_in_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
    # Inputs are simulation-wide: make the legacy cases' fallback explicit
    # before batching them with the distinct-claimability cases.
    swap_units = [
        {**unit, "claimable": unit["claimed"], "exception": (False, False)}
        for unit in units
    ] + _claimability_cases()
    check_swap(swap_units, year, OUTPUTS, _identities(swap_units))
    check_monotone(units, year, MONOTONE, _identities(units))
