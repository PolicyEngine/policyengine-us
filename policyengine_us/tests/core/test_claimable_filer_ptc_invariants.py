"""The premium tax credit for a filer who can be claimed as a dependent.

Someone another taxpayer can claim is not an applicable taxpayer (IRC
36B(c)(1)(D)) and is outside the tax family (26 CFR 1.36B-1(d)(2)); a return
with such a filer claims no dependents (IRC 152(b)(1)). The credit therefore
uses `aca_tax_family_size` for the poverty line and the coverage family's
benchmark `aca_ptc_slcsp`, and the state premium programs that wrap it follow.

For couples drawn by Hypothesis and a seeded population, with either, both or
neither spouse claimed:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Identities: `aca_tax_family_size` equals the filers who cannot be claimed
   plus the dependents when no filer can be claimed; nobody outside the tax
   family is eligible; 0 <= `aca_ptc_slcsp` <= `slcsp`; a return where every
   filer can be claimed has no credit; and a return where no filer can be
   claimed keeps `slcsp`, the tax unit size and the tax unit's poverty line.
3. Monotonicity: marking another filer as claimed never raises the tax family
   size, never raises the benchmark while the enrollees stay the same, and
   never raises the credit of a return that had an eligible member. Both can
   rise otherwise, as intended: a couple below 100% of the two-person line can
   be above it for a tax family of one, so IRC 36B allows the credit and the
   unclaimable spouse leaves the coverage gap that pays_aca_premium assumes
   nobody buys into.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    CLAIM_PATTERNS,
    TOLERANCE,
    _calc,
    _crafted_cases,
    _monotone_variants,
    _seeded_couples,
    _situation,
    _swap_variants,
    adults,
    dependents,
)

# Texas (age curve, no expansion), New York and Vermont (family tiers), and
# the states whose premium programs wrap the credit.
STATES = ["TX", "NY", "VT", "MA", "CT", "CO", "MD", "CA", "NM", "NJ", "WA"]
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
FEDERAL = [
    "aca_tax_family_size",
    "aca_fpg",
    "aca_magi_fraction",
    "slcsp",
    "aca_ptc_slcsp",
    "aca_ptc",
    "marketplace_csr_eligible",
]
STATE_WRAPS = [
    "ma_connector_care",
    "ct_covered_connecticut",
    "co_premium_assistance",
    "md_premium_assistance",
    "ca_premium_subsidy",
    "nm_premium_assistance",
    "vt_premium_assistance",
    "nj_njhps",
    "wa_cascade_care_savings",
]
OUTPUTS = FEDERAL + STATE_WRAPS


@st.composite
def couples(draw):
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": draw(st.sampled_from(CLAIM_PATTERNS)),
    }


def _ptc_cases(states):
    # Two 30-year-olds whose income is 150% of the one-person line in 2025,
    # with and without a child: the credit for the unclaimable spouse.
    adult = {"age": 30, "employment_income": 11_295.0}
    cases = []
    for state in states:
        for claimed in [(True, False), (True, True)]:
            cases += [
                {
                    "state": state,
                    "adults": [adult, adult],
                    "dependents": [],
                    "claimed": claimed,
                },
                {
                    "state": state,
                    "adults": [adult, adult],
                    "dependents": [{"age": 4}],
                    "claimed": claimed,
                },
            ]
    return cases


def _tax_unit_sum(sim, name, year):
    return np.asarray(sim.calculate(name, year, map_to="tax_unit"), dtype=float)


def _identities(sim, year):
    claimed_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    independent = _calc(sim, "head_spouse_count_not_dependent_elsewhere", year)
    dependents_count = _calc(sim, "tax_unit_count_dependents", year)
    size = _calc(sim, "aca_tax_family_size", year)
    np.testing.assert_array_equal(
        size, independent + np.where(claimed_filer, 0, dependents_count)
    )
    eligible = np.asarray(sim.calculate("is_aca_ptc_eligible", year))
    member = np.asarray(sim.calculate("is_aca_tax_family_member", year))
    assert not (eligible & ~member).any(), "an eligible person is outside the family"
    slcsp = _calc(sim, "slcsp", year)
    benchmark = _calc(sim, "aca_ptc_slcsp", year)
    assert (benchmark >= -TOLERANCE).all()
    assert (benchmark <= slcsp + TOLERANCE).all(), "benchmark above slcsp"
    nobody_in_family = size == 0
    assert not _calc(sim, "aca_ptc", year)[nobody_in_family].any()
    unclaimed = ~claimed_filer
    np.testing.assert_allclose(benchmark[unclaimed], slcsp[unclaimed], atol=TOLERANCE)
    np.testing.assert_array_equal(
        size[unclaimed], _calc(sim, "tax_unit_size", year)[unclaimed]
    )
    np.testing.assert_allclose(
        _calc(sim, "aca_fpg", year)[unclaimed],
        _calc(sim, "tax_unit_fpg", year - 1)[unclaimed],
    )


def check_swap(units, year, outputs, require_coverage=False):
    sim = Simulation(situation=_situation(units, year, _swap_variants))
    if require_coverage:
        # The batch must reach the rule: returns with exactly one claimable
        # filer that still get a credit and, from 2026 when the modeled state
        # programs start, a state wrap paid on one.
        one_claimed = (
            _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
        ) & (_calc(sim, "head_spouse_count_not_dependent_elsewhere", year) == 1)
        assert (_calc(sim, "aca_ptc", year)[one_claimed] > 0).any()
        if year >= 2026:
            wraps = sum(_calc(sim, name, year) for name in STATE_WRAPS)
            assert (wraps[one_claimed] > 0).any()
    values = {name: _calc(sim, name, year) for name in outputs}
    values["eligible members"] = _tax_unit_sum(sim, "is_aca_ptc_eligible", year)
    for name, value in values.items():
        assert np.isfinite(value).all(), f"{name} in {year} is not finite"
        drawn, swapped = value[0::2], value[1::2]
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
    _identities(sim, year)


def check_monotone(units, year):
    sim = Simulation(situation=_situation(units, year, _monotone_variants))
    had_eligible = (_tax_unit_sum(sim, "is_aca_ptc_eligible", year) > 0).reshape(-1, 4)
    enrollees = _tax_unit_sum(sim, "pays_aca_premium", year).reshape(-1, 4)
    for name, guard in (
        ("aca_tax_family_size", None),
        ("aca_ptc_slcsp", "same enrollees"),
        ("aca_ptc", "had eligible"),
    ):
        values = _calc(sim, name, year).reshape(-1, 4)
        nobody, first, second, both = values.T
        for more, fewer, base, label in (
            (first, nobody, 0, "first adult"),
            (second, nobody, 0, "second adult"),
            (both, first, 1, "both after first"),
            (both, second, 2, "both after second"),
        ):
            rises = more > fewer + TOLERANCE
            if guard == "had eligible":
                rises &= had_eligible[:, base]
            elif guard == "same enrollees":
                more_index = {"first adult": 1, "second adult": 2}.get(label, 3)
                rises &= enrollees[:, base] == enrollees[:, more_index]
            assert not rises.any(), (
                f"{name} in {year} rises when the {label} is claimed "
                "elsewhere: "
                + ", ".join(
                    f"{units[i]['state']} {fewer[i]:.2f} -> {more[i]:.2f}"
                    for i in np.flatnonzero(rises)[:10]
                )
            )
    _identities(sim, year)


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(couples(), min_size=6, max_size=15))
def test_claimable_filer_ptc_is_label_free(year, units):
    check_swap(units, year, OUTPUTS)


@pytest.mark.parametrize("year", [2025, 2026])
def test_claimable_filer_ptc_seeded_population(year):
    units = (
        _seeded_couples(STATES, per_state=2)
        + _crafted_cases(STATES, review_case_only=True)
        + _ptc_cases(STATES)
    )
    check_swap(units, year, OUTPUTS, require_coverage=True)
    check_monotone(units, year)
