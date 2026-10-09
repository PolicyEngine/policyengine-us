"""New Mexico rules for a filer who can be claimed as a dependent.

The child income tax credit, the 65+ medical care credit and exemption, the
working families credit, the elderly property tax rebate, the child day care
credit, the 100+ exemption and the deduction for certain dependents apply
NMSA chapter 7 article 2's "not a dependent of another individual" tests per
filer, and count no dependents on a return with a claimable filer.

For couples drawn by Hypothesis and a seeded population in NM, with
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
    units = _seeded_couples(STATES, per_state=3) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS)
    check_monotone(units, year, OUTPUTS)
