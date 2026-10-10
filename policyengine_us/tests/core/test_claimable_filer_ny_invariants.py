"""New York rules for a filer who can be claimed as a dependent.

The household credit, real property tax credit, dependent exemptions, college
tuition, 2023 inflation refund and 2026 child and dependent care credit apply
Tax Law 606 and 616's dependent tests.

For couples with either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling (Hypothesis batches, the seeded population and the crafted
   tuition cases).
2. Monotonicity: marking another filer as claimed never raises an output
   (seeded population and crafted cases only).

The crafted cases give both spouses and a dependent student tuition, which the
generated population never has. The New York City credits need a New York City
household and, like the contributed reforms, are covered by YAML cases only.
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

STATES = ["NY"]
YEARS = [2023, 2025, 2026]
OUTPUTS = [
    "ny_household_credit_potential",
    "ny_real_property_tax_credit",
    "ny_exemptions",
    "ny_allowable_college_tuition_expenses",
    "ny_inflation_refund_credit",
    "ny_cdcc",
]


def _tuition_cases():
    # Both spouses and a dependent student with tuition, with and without a
    # young child and childcare expenses.
    first = {
        "age": 45,
        "employment_income": 20_000.0,
        "qualified_tuition_expenses": 6_000.0,
    }
    second = {
        "age": 44,
        "employment_income": 12_000.0,
        "qualified_tuition_expenses": 3_000.0,
    }
    student = {
        "age": 19,
        "is_full_time_student": True,
        "qualified_tuition_expenses": 8_000.0,
    }
    child = {"age": 3, "pre_subsidy_childcare_expenses": 4_000.0}
    return [
        {
            "state": "NY",
            "adults": [first, second],
            "dependents": others,
            "claimed": claimed,
        }
        for others in ([], [student], [student, child])
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
def test_ny_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS)


@pytest.mark.parametrize("year", YEARS)
def test_ny_claimable_filer_rules_seeded_population(year):
    units = (
        _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES) + _tuition_cases()
    )
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, OUTPUTS)
