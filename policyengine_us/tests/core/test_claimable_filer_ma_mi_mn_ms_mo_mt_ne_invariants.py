"""Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Montana and
Nebraska rules for a filer who can be claimed as a dependent.

A return on which the filer, or on a joint return either spouse, can be
claimed as a dependent has no dependents (IRC 152(b)(1)), so the dependent
exemptions and credits that require a dependent of the taxpayer are zero; the
filers' own exemptions and the routes that ignore 152(b)(1) (an IRC 21
qualifying individual incapable of self-care) remain. Rules that bar the
claimable individual (Michigan's heating exemption, Nebraska's personal
exemption credit, Massachusetts' senior circuit breaker, Montana's 2021
rebate) apply per filer, and Minnesota's dependent standard deduction
worksheet applies when either spouse can be claimed.

For couples drawn by Hypothesis and a seeded population in these states, with
either, both or neither spouse claimed:

1. Swap invariance: each output, and state income tax, is the same under
   either head/spouse labelling.
2. Monotonicity: marking another filer as claimed never raises an output.
3. Identities: on a return with a claimable filer, the dependent amounts are
   zero (the drawn dependents are never incapable of self-care).
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
    _calc,
    _crafted_cases,
    _seeded_couples,
    adults,
    dependents,
)

STATES = ["MA", "MI", "MN", "MS", "MO", "MT", "NE"]
YEARS = [2021, 2024, 2026]
# Amounts that marking another filer as claimed must never raise.
MONOTONE = [
    "ma_income_tax_exemption_threshold",
    "ma_senior_circuit_breaker",
    "ma_child_and_family_credit",
    "ma_qualified_unemployment_deduction",
    "ma_eitc",
    "mi_exemptions_count",
    "mi_home_heating_credit",
    "mi_eitc",
    "mn_standard_deduction",
    "mn_exemptions",
    "mn_child_and_working_families_credits",
    "mn_cdcc",
    "ms_dependents_exemption",
    "ms_cdcc",
    "mo_wftc_potential",
    "ne_exemptions",
    "ne_stillborn_credit",
    "ne_refundable_ctc",
    "ne_eitc",
    "ne_cdcc_refundable",
]
# The Massachusetts exemption also adds the federal medical deduction when the
# filers itemize, which a lower federal standard deduction can switch on, so
# it is checked for swap invariance only.
OUTPUTS = MONOTONE + ["ma_part_b_taxable_income_exemption", "state_income_tax"]
# Zero on a return with a claimable filer.
DEPENDENT_AMOUNTS = [
    "ms_dependents_exemption",
    "mn_exemptions",
    "mn_cdcc_dependent_count",
    "ne_stillborn_credit",
    "ne_refundable_ctc",
    "ma_child_and_family_credit",
]


def _identities(sim, year):
    claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    for name in DEPENDENT_AMOUNTS:
        values = _calc(sim, name, year)
        assert not values[claimed_filer].any(), (
            f"{name} in {year} is positive on a return with a claimable filer"
        )


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
def test_claimable_filer_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _identities)


@pytest.mark.parametrize("year", YEARS)
def test_claimable_filer_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=2) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _identities)
    check_monotone(units, year, MONOTONE, _identities)
