"""Federal rules for a filer who can be claimed as a dependent elsewhere.

A filer who can be claimed as a dependent on another return is treated as
having no dependents (IRC 152(b)(1); on a joint return, if either spouse can be
claimed, "you and your spouse can't claim any dependents", Publication 501) and
has no personal exemption (IRC 151(d)(2)). So:

- `exemptions_count` counts only the filers who cannot be claimed, plus the
  dependents when no filer can be claimed;
- `ctc_qualifying_child` and the credit for other dependents are zero on a
  return with a claimable filer;
- a child under 13 is not a child and dependent care qualifying person on such
  a return (a disabled person still is, IRC 21(b)(1)(B));
- recovery rebates leave out a claimable filer and, on such a return, the
  dependents.

For couples drawn by Hypothesis and a seeded population, with either, both or
neither spouse claimed, in 2021-2026:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Monotonicity: marking another filer as claimed never raises any of the
   amounts or counts below.
3. Identities: `exemptions_count` equals the filers who cannot be claimed plus
   the dependents when no filer can be claimed, and a return with a claimable
   filer has no CTC-qualifying child and no credit for other dependents.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    TOLERANCE,
    YEARS,
    _calc,
    _crafted_cases,
    _monotone_variants,
    _seeded_couples,
    _situation,
    _swap_variants,
    adults,
    dependents,
)

# Texas has no income tax; the others read the federal exemption count.
STATES = ["TX", "OR", "HI", "NM", "GA", "RI", "DE", "OH", "WI"]
OUTPUTS = [
    "income_tax",
    "ctc_maximum",
    "ctc_qualifying_children",
    "capped_count_cdcc_eligible",
    "exemptions_count",
    "rrc_arpa",
]
# Amounts that marking another filer as claimed must never raise.
MONOTONE = [
    "ctc_maximum",
    "ctc_qualifying_children",
    "capped_count_cdcc_eligible",
    "exemptions_count",
    "rrc_arpa",
]


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def check_swap(units, year, outputs, identities=None):
    """Each output is the same under either head/spouse labelling."""
    sim = Simulation(situation=_situation(units, year, _swap_variants))
    for name in outputs:
        values = _calc(sim, name, year)
        assert np.isfinite(values).all(), f"{name} in {year} is not finite"
        drawn, swapped = values[0::2], values[1::2]
        differs = ~(np.abs(swapped - drawn) <= TOLERANCE)
        assert not differs.any(), (
            f"{name} in {year} changes when the head and spouse labels are "
            "exchanged: "
            + ", ".join(
                f"{units[i]['state']} claimed={units[i]['claimed']} "
                f"{drawn[i]:.2f} -> {swapped[i]:.2f}"
                for i in np.flatnonzero(differs)[:10]
            )
        )
    if identities is not None:
        identities(sim, year)


def check_monotone(units, year, outputs, identities=None):
    """Marking another filer as claimed never raises an output."""
    sim = Simulation(situation=_situation(units, year, _monotone_variants))
    for name in outputs:
        values = _calc(sim, name, year).reshape(-1, 4)
        nobody, first, second, both = values.T
        for more, fewer, label in (
            (first, nobody, "first adult"),
            (second, nobody, "second adult"),
            (both, first, "both after first"),
            (both, second, "both after second"),
        ):
            rises = more > fewer + TOLERANCE
            assert not rises.any(), (
                f"{name} in {year} rises when the {label} is claimed "
                "elsewhere: "
                + ", ".join(
                    f"{units[i]['state']} {fewer[i]:.2f} -> {more[i]:.2f}"
                    for i in np.flatnonzero(rises)[:10]
                )
            )
    if identities is not None:
        identities(sim, year)


def _federal_identities(sim, year):
    claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    independent = _calc(sim, "head_spouse_count_not_dependent_elsewhere", year)
    dependents_count = _calc(sim, "tax_unit_count_dependents", year)
    expected = independent + np.where(claimed_filer, 0, dependents_count)
    np.testing.assert_array_equal(_calc(sim, "exemptions_count", year), expected)
    assert not _calc(sim, "ctc_qualifying_children", year)[claimed_filer].any()
    odc = np.asarray(
        sim.calculate("ctc_adult_individual_maximum", year, map_to="tax_unit")
    )
    assert not odc[claimed_filer].any()


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=15))
def test_claimable_filer_federal_rules_are_label_free(year, units):
    check_swap(units, year, OUTPUTS, _federal_identities)


@pytest.mark.parametrize("year", YEARS)
def test_claimable_filer_federal_rules_seeded_population(year):
    units = _seeded_couples(STATES, per_state=2) + _crafted_cases(STATES)
    check_swap(units, year, OUTPUTS, _federal_identities)
    check_monotone(units, year, MONOTONE, _federal_identities)
