"""New Mexico rules for a filer who can be claimed as a dependent.

Several credits and exemptions bar "a dependent of another individual", and
dependent-based amounts need dependents that a return with a claimable filer
cannot have (IRC 152(b)(1)).

For couples with either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling (Hypothesis batches, the seeded population and the crafted
   centenarian cases).
2. Monotonicity: marking another filer as claimed never raises an output
   (seeded population and crafted cases only).

The crafted cases add spouses aged 100 or older, whom the generated population
(ages 18 to 90) never has.
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
)

STATES = ["NM"]
YEARS = [2023, 2025, 2026]
OUTPUTS = [
    "nm_ctc",
    "nm_medical_expense_credit",
    "nm_medical_expense_exemption",
    "nm_eitc",
    "nm_deduction_for_certain_dependents",
    "nm_property_tax_rebate",
    "nm_cdcc_max_amount",
    "nm_hundred_year_exemption",
]


def _centenarian_cases():
    # One or both spouses aged 100 or older, with income to exempt.
    centenarian = {"age": 101, "taxable_pension_income": 20_000.0}
    older = {"age": 103, "taxable_interest_income": 5_000.0}
    younger = {"age": 70, "social_security_retirement": 12_000.0}
    return [
        {
            "state": "NM",
            "adults": couple,
            "dependents": [],
            "claimed": claimed,
        }
        for couple in ([centenarian, younger], [centenarian, older])
        for claimed in [(True, False), (False, True), (True, True)]
    ]


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
def test_nm_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS)


@pytest.mark.parametrize("year", YEARS)
def test_nm_claimable_filer_rules_seeded_population(year):
    units = (
        _seeded_couples(STATES, per_state=3)
        + _crafted_cases(STATES)
        + _centenarian_cases()
    )
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, OUTPUTS)
