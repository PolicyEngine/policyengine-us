"""Arizona, Arkansas and California rules for a filer who can be claimed as a
dependent.

Arizona's dependent and family credits, excise credit and 2021 families
rebate, Arkansas's dependent, disabled-dependent and low-income-table rules,
and California's standard deduction, exemption credits, CalEITC, foster youth
credit and renter credit apply IRC 151(d)(2) and 152(b)(1) and each state's
own text.

For couples drawn by Hypothesis, a seeded population and crafted cases in the
three states (renters who lived with the person who can claim them, and a
disabled dependent who is a filer's own child, someone else's child, or of
unknown relationship), with either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises a credit,
   deduction or eligibility below.
3. Identities: a return with a claimable filer gets no Arizona dependent
   credit or families rebate and no Arkansas dependent credit, and a return
   on which every filer can be claimed gets no Arizona excise credit.
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

STATES = ["AZ", "AR", "CA"]
# 2021 covers the Arizona families rebate; 2026 the new Arizona amounts.
YEARS = [2021, 2023, 2025, 2026]
MONOTONE = [
    "az_dependent_tax_credit_potential",
    "az_family_tax_credit_eligible",
    "az_family_tax_credit_potential",
    "az_increased_excise_tax_credit",
    "az_families_tax_rebate",
    "ar_personal_credits_potential",
    "ca_standard_deduction",
    "ca_exemptions",
    "ca_eitc_eligible",
    "ca_eitc",
    "ca_foster_youth_tax_credit",
    "ca_renter_credit",
]
# Arkansas's tax can rise when the low-income table changes, so it is checked
# only for swap invariance.
OUTPUTS = MONOTONE + [
    "ar_income_tax_before_non_refundable_credits_unit",
    "state_income_tax",
]


def _identities(sim, year):
    claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    every_filer = _calc(sim, "every_filer_is_dependent_elsewhere", year) > 0
    for name in ["az_dependent_tax_credit_potential", "az_families_tax_rebate"]:
        assert not _calc(sim, name, year)[claimed_filer].any(), name
    ar_dependent = np.asarray(
        sim.calculate("ar_personal_credit_dependent", year, map_to="tax_unit")
    )
    assert not ar_dependent[claimed_filer].any()
    assert not _calc(sim, "az_increased_excise_tax_credit", year)[every_filer].any()


def _claimable_rule_cases():
    """Cases for the inputs the shared strategies never set."""
    renter = {
        "age": 20,
        "employment_income": 2_000.0,
        "rent": 6_000.0,
        "lives_with_claiming_taxpayer": True,
    }
    earner = {"age": 30, "person_id": 1, "employment_income": 20_000.0}
    cases = []
    for state in STATES:
        for claimed in CLAIM_PATTERNS:
            cases.append(
                {
                    "state": state,
                    "adults": [
                        {**renter, "person_id": 1},
                        {**renter, "person_id": 2, "age": 22},
                    ],
                    "dependents": [],
                    "claimed": claimed,
                }
            )
            # Parent id 1 is the first adult; 99 is a parent outside the
            # household; no id leaves the relationship unknown.
            for parent in (1, 99, None):
                dependent = {"age": 8, "is_disabled": True, "person_id": 3}
                if parent is not None:
                    dependent["parent_1_id"] = parent
                cases.append(
                    {
                        "state": state,
                        "adults": [earner, {"age": 32, "person_id": 2}],
                        "dependents": [dependent],
                        "claimed": claimed,
                    }
                )
    return cases


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=12))
def test_az_ar_ca_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_az_ar_ca_claimable_filer_rules_seeded_population(year):
    units = (
        _seeded_couples(STATES, per_state=3)
        + _crafted_cases(STATES)
        + _claimable_rule_cases()
    )
    check_swap(units, year, OUTPUTS, _identities)
    check_monotone(units, year, MONOTONE, _identities)
