"""Oregon, Maine and Hawaii rules for a filer who can be claimed as a dependent.

Exemptions and dependent-based credits leave out a claimable filer and, where
the law needs a dependent, a return on which a filer can be claimed.

For couples drawn by Hypothesis and a seeded population in OR, ME, HI, with
either, both or neither spouse claimed, each output is the same under either
head/spouse labelling, and marking another filer as claimed never raises it.
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
    units = _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, OUTPUTS)
