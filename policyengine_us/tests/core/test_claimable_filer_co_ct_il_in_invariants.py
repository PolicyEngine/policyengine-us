"""Colorado, Connecticut, Illinois and Indiana rules for a filer who can be
claimed as a dependent.

A return on which the filer, or on a joint return either spouse, can be claimed
as a dependent has no dependents (IRC 152(b)(1)), so it gets no state
dependent exemption, child credit or child-based deduction, and a childless
filer who can be claimed gets no state EITC through the ITIN or age extensions
(IRC 32(c)(1)(A)(ii)(III)). Indiana keeps each filer's own $1,000 exemption.

For couples drawn by Hypothesis and a seeded population in these states, with
either, both or neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises the outputs in
   MONOTONE (amounts not capped by a tax liability that the claim can raise).
3. Identities: a return with a claimable filer has no Illinois dependent
   exemption, Colorado or Illinois child tax credit or Indiana additional
   exemption, and its Indiana base exemptions are $1,000 per filer.
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
    "in_base_exemptions",
    "in_additional_exemptions",
    "in_adoption_exemption",
]
OUTPUTS = MONOTONE + ["co_refundable_credits"]


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def _identities(units):
    states = np.array([unit["state"] for unit in units])

    def check(sim, year):
        claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
        # Each unit is simulated as consecutive copies (labellings or claim
        # patterns), in the order of the units.
        state = np.repeat(states, len(claimed_filer) // len(units))
        for name in (
            "il_dependent_exemption",
            "co_ctc",
            "il_ctc",
            "in_additional_exemptions",
        ):
            assert not _calc(sim, name, year)[claimed_filer].any(), (
                f"{name} in {year} is positive on a return with a claimable filer"
            )
        filers = _calc(sim, "tax_unit_size", year) - _calc(
            sim, "tax_unit_dependents", year
        )
        base = _calc(sim, "in_base_exemptions", year)
        mask = claimed_filer & (state == "IN")
        np.testing.assert_array_equal(base[mask], 1_000 * filers[mask])

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
    check_swap(units, year, OUTPUTS, _identities(units))
    check_monotone(units, year, MONOTONE, _identities(units))
