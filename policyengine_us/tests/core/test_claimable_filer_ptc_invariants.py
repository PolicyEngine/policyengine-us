"""The premium tax credit for a filer who can be claimed as a dependent.

No credit is allowed to someone another taxpayer can claim (IRC 36B(c)(1)(D));
such a spouse is outside the tax family (26 CFR 1.36B-1(d)(2)), and a return
with such a filer claims no dependents (IRC 152(b)(1)) unless the would-be
claimant meets the refund-only filing exception. The credit therefore uses
`aca_tax_family_size` for the poverty line, household income without
out-of-family dependents (`aca_magi`), the coverage family's benchmark
(`aca_ptc_slcsp`) and its share of the premium
(`aca_ptc_coverage_family_premium`), and the state premium programs that wrap
it follow.

For couples drawn by Hypothesis in every year 2021-2026 (spouses claimable,
actually claimed or neither, with or without the filing exception) and a
seeded population in 2025 and 2026:

1. Swap invariance: each output is the same under either head/spouse
   labelling.
2. Identities: `aca_tax_family_size` equals the filers who cannot be claimed
   plus the dependents when one of them is an applicable taxpayer and no
   filer is claimable outside the exception; nobody outside the tax family is
   eligible; 0 <= `aca_ptc_slcsp` <= `slcsp`; `aca_magi` <= `medicaid_magi`;
   used credit <= coverage-family premium <= selected premium; cost-sharing
   reductions only when every enrollee is eligible for the credit; no family
   member means no credit; and where no filer can be claimed, `aca_ptc_slcsp`
   = `slcsp`, `aca_magi` = `medicaid_magi`, `aca_tax_family_size` =
   `tax_unit_size` and `aca_fpg` = `tax_unit_fpg` for the prior year (these
   simulations supply no prior-year size, so the two sizes agree).
3. Monotonicity: marking another filer as claimed never raises the tax family
   size, never raises the benchmark while the same people are enrolled, and
   never raises the credit, except in two intended cases: income crosses the
   100% floor (below it for two, above it for one, so IRC 36B allows a credit
   that was not allowed), or out-of-family dependents' income leaves household
   income.
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
    "aca_magi",
    "aca_magi_fraction",
    "slcsp",
    "aca_ptc_slcsp",
    "aca_ptc",
    "aca_ptc_coverage_family_premium",
    "used_aca_ptc",
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
    claimed = draw(st.sampled_from(CLAIM_PATTERNS))
    # Claimable whenever claimed, and sometimes claimable but not claimed.
    extra = draw(st.sampled_from(CLAIM_PATTERNS))
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()), draw(adults())],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": claimed,
        "claimable": (claimed[0] or extra[0], claimed[1] or extra[1]),
        "exception": draw(st.sampled_from(CLAIM_PATTERNS)),
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


def _tax_unit_sum_array(sim, values):
    tax_units = sim.populations["tax_unit"]
    return np.bincount(
        np.asarray(tax_units.members_entity_id),
        weights=np.asarray(values, dtype=float),
        minlength=tax_units.count,
    )


def _enrollment_signature(sim, year):
    # Which members are enrolled, as one number per tax unit, so variants
    # can be compared person by person rather than by count.
    position = np.asarray(sim.populations["tax_unit"].members_position)
    enrolled = np.asarray(sim.calculate("pays_aca_premium", year), dtype=float)
    return _tax_unit_sum_array(sim, enrolled * 2.0**position)


def _identities(sim, year):
    claimable_filer = _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
    blocked = (
        _calc(
            sim, "head_or_spouse_is_dependent_elsewhere_without_filing_exception", year
        )
        > 0
    )
    independent = _calc(sim, "head_spouse_count_not_dependent_elsewhere", year)
    dependents_count = _calc(sim, "tax_unit_count_dependents", year)
    size = _calc(sim, "aca_tax_family_size", year)
    claims_dependents = (independent > 0) & ~blocked
    np.testing.assert_array_equal(
        size, independent + np.where(claims_dependents, dependents_count, 0)
    )
    eligible = np.asarray(sim.calculate("is_aca_ptc_eligible", year))
    member = np.asarray(sim.calculate("is_aca_tax_family_member", year))
    assert not (eligible & ~member).any(), "an eligible person is outside the family"
    slcsp = _calc(sim, "slcsp", year)
    benchmark = _calc(sim, "aca_ptc_slcsp", year)
    assert (benchmark >= -TOLERANCE).all()
    assert (benchmark <= slcsp + TOLERANCE).all(), "benchmark above slcsp"
    aca_magi = _calc(sim, "aca_magi", year)
    medicaid_magi = _calc(sim, "medicaid_magi", year)
    assert (aca_magi <= medicaid_magi + TOLERANCE).all()
    premium = _calc(sim, "selected_marketplace_plan_premium_proxy", year)
    family_premium = _calc(sim, "aca_ptc_coverage_family_premium", year)
    used = _calc(sim, "used_aca_ptc", year)
    assert (used <= family_premium + TOLERANCE).all()
    assert (family_premium <= premium + TOLERANCE).all()
    csr = _calc(sim, "marketplace_csr_eligible", year) > 0
    enrolled = np.asarray(sim.calculate("pays_aca_premium", year))
    ineligible_enrollees = _tax_unit_sum_array(sim, enrolled & ~eligible)
    assert not (csr & (ineligible_enrollees > 0)).any()
    assert not _calc(sim, "aca_ptc", year)[size == 0].any()
    unclaimed = ~claimable_filer
    np.testing.assert_allclose(benchmark[unclaimed], slcsp[unclaimed], atol=TOLERANCE)
    np.testing.assert_allclose(
        aca_magi[unclaimed], medicaid_magi[unclaimed], atol=TOLERANCE
    )
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
        one_claimable = (
            _calc(sim, "head_or_spouse_is_dependent_elsewhere", year) > 0
        ) & (_calc(sim, "head_spouse_count_not_dependent_elsewhere", year) == 1)
        assert (_calc(sim, "aca_ptc", year)[one_claimable] > 0).any()
        if year >= 2026:
            wraps = sum(_calc(sim, name, year) for name in STATE_WRAPS)
            assert (wraps[one_claimable] > 0).any()
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
    fraction = _calc(sim, "aca_magi_fraction", year).reshape(-1, 4)
    magi = _calc(sim, "aca_magi", year).reshape(-1, 4)
    enrollees = _enrollment_signature(sim, year).reshape(-1, 4)
    for name in ("aca_tax_family_size", "aca_ptc_slcsp", "aca_ptc"):
        values = _calc(sim, name, year).reshape(-1, 4)
        for more, fewer, label in (
            (1, 0, "first adult"),
            (2, 0, "second adult"),
            (3, 1, "both after first"),
            (3, 2, "both after second"),
        ):
            rises = values[:, more] > values[:, fewer] + TOLERANCE
            if name == "aca_ptc_slcsp":
                rises &= enrollees[:, more] == enrollees[:, fewer]
            if name == "aca_ptc":
                crosses_floor = (fraction[:, fewer] < 1) & (fraction[:, more] >= 1)
                income_left = magi[:, more] < magi[:, fewer] - TOLERANCE
                rises &= ~crosses_floor & ~income_left
            assert not rises.any(), (
                f"{name} in {year} rises when the {label} is claimed "
                "elsewhere: "
                + ", ".join(
                    f"{units[i]['state']} {values[i, fewer]:.2f} -> "
                    f"{values[i, more]:.2f}"
                    for i in np.flatnonzero(rises)[:10]
                )
            )
    _identities(sim, year)


@pytest.mark.parametrize("year", YEARS)
@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(couples(), min_size=6, max_size=15))
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
