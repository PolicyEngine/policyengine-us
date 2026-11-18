"""Oregon, Maine and Hawaii rules for a filer who can be claimed as a dependent.

Each state denies such a filer their own exemption, and several credits need
dependents that a return with a claimable filer cannot have (IRC 152(b)(1)).

For couples with either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling (Hypothesis batches, the seeded population and the crafted
   incapacity cases).
2. Monotonicity: marking another filer as claimed never raises an output
   (seeded population and crafted cases only).

The crafted cases add adults and a dependent who are incapable of self-care,
with care expenses, which the generated population never has. The contributed
reforms and the Oregon credit's column are covered by YAML cases only.
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

STATES = ["OR", "ME", "HI"]
YEARS = [2021, 2025, 2026]
OUTPUTS = [
    "or_exemption_credit",
    "or_ctc",
    "or_wfhdc_has_qualified_individual_eligible",
    "me_personal_exemption_deduction",
    "me_dependent_exemption_credit",
    "me_pro_forma_childless_eitc",
    "me_relief_rebate",
    "me_property_tax_fairness_credit_benefit_base",
    "hi_regular_exemptions",
    "hi_disabled_exemptions",
    "hi_cdcc_eligible",
    "hi_cdcc_qualifying_individuals",
    "hi_cdcc",
]


def _incapacity_cases():
    # Both spouses and an adult dependent incapable of self-care, with care
    # expenses, and a young child with childcare expenses.
    earner = {
        "age": 45,
        "employment_income": 10_000.0,
        "is_disabled": True,
        "is_incapable_of_self_care": True,
        "pre_subsidy_care_expenses": 2_000.0,
    }
    other = {
        "age": 44,
        "employment_income": 3_000.0,
        "is_disabled": True,
        "is_incapable_of_self_care": True,
        "pre_subsidy_care_expenses": 1_000.0,
    }
    relative = {
        "age": 30,
        "is_disabled": True,
        "is_incapable_of_self_care": True,
        "pre_subsidy_care_expenses": 1_500.0,
    }
    child = {"age": 4, "pre_subsidy_childcare_expenses": 3_000.0}
    return [
        {
            "state": state,
            "adults": couple,
            "dependents": others,
            "claimed": claimed,
        }
        for state in ("OR", "HI")
        for couple in ([earner, other], [earner, {"age": 44}])
        for others in ([], [child], [child, relative])
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
def test_or_me_hi_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS)


@pytest.mark.parametrize("year", YEARS)
def test_or_me_hi_claimable_filer_rules_seeded_population(year):
    units = (
        _seeded_couples(STATES, per_state=3)
        + _crafted_cases(STATES)
        + _incapacity_cases()
    )
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, OUTPUTS)
