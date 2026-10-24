"""Medicare IRMAA schedules: invariants across the years the model covers.

42 U.S.C. 1395r(i) sets the Part B income-related monthly adjustment amounts
and their income thresholds, and 42 U.S.C. 1395w-113(a)(7) applies the same
thresholds and applicable percentages to Part D. Checked for every year from
FIRST_MODELED_YEAR through 2035:

- every schedule starts with a zero amount at zero income, its thresholds rise
  strictly until any unreachable (+inf) bracket, and its amounts never fall
  from one tier to the next;
- head of household and surviving spouse filers use the single schedule, since
  1395r(i)(2)(A) sets one threshold amount for every return but a joint one;
- Part D uses the Part B thresholds.

Checked for the years CMS has published schedules for (2015-2026):

- joint thresholds are twice the individual ones, except the $500,000 amount,
  which is 150 percent (1395r(i)(3)(C)(ii));
- a married individual filing separately who lived with the spouse is charged,
  once MAGI exceeds the individual threshold amount, what the individual
  schedule charges at MAGI plus that amount, since 1395r(i)(3)(C)(iii) reduces
  each individual dollar amount by it;
- each Part B adjustment is (applicable percentage - 25) / 25 times the
  standard premium: 1395r(i)(3)(A) multiplies the percentage less 25 points by
  200 percent of the aged actuarial rate (plus 4 times any repayment amount),
  and 1395r(a)(3) and (a)(6) set the premium at 50 percent of that rate plus
  the repayment amount;
- each Part D adjustment is the base beneficiary premium times (applicable
  percentage - 25.5) / 25.5 (1395w-113(a)(7)(B)), so the tiers are in that
  proportion to one another.

The last two hold up to the rounding of each published amount to the dime.
"""

import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

MEDICARE = system.parameters.gov.hhs.medicare
PARTS = ["part_b", "part_d"]
STATUSES = ["single", "head_of_household", "surviving_spouse", "joint", "separate"]
ALL_YEARS = list(range(FIRST_MODELED_YEAR, 2036))
PUBLISHED_YEARS = list(range(2015, 2027))
# Applicable percentages of the five tiers above the standard premium
# (1395r(i)(3)(C)(i)); the 85 percent tier starts in 2019.
APPLICABLE_PERCENTAGES = [35, 50, 65, 80, 85]
PART_B_TOLERANCE = 0.25
PART_D_TOLERANCE = 0.10


def schedule(part, status, year):
    return getattr(getattr(MEDICARE, part).irmaa, status)(f"{year}-01-01")


def reachable_tiers(scale):
    """(applicable percentage, amount) for each finite tier above zero."""
    tiers = [
        amount
        for threshold, amount in zip(scale.thresholds[1:], scale.amounts[1:])
        if math.isfinite(threshold)
    ]
    return list(zip(APPLICABLE_PERCENTAGES, tiers))


@pytest.mark.parametrize("year", ALL_YEARS)
@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("part", PARTS)
def test_schedule_is_ordered(part, status, year):
    scale = schedule(part, status, year)
    thresholds, amounts = list(scale.thresholds), list(scale.amounts)
    assert thresholds[0] == 0 and amounts[0] == 0
    finite = [t for t in thresholds if math.isfinite(t)]
    assert thresholds[: len(finite)] == finite, "+inf brackets come last"
    assert all(a < b for a, b in zip(finite, finite[1:]))
    assert all(a <= b for a, b in zip(amounts, amounts[1:]))


@pytest.mark.parametrize("year", ALL_YEARS)
@pytest.mark.parametrize("status", ["head_of_household", "surviving_spouse"])
@pytest.mark.parametrize("part", PARTS)
def test_other_unmarried_filers_use_the_single_schedule(part, status, year):
    scale, single = schedule(part, status, year), schedule(part, "single", year)
    assert list(scale.thresholds) == list(single.thresholds)
    assert list(scale.amounts) == list(single.amounts)


@pytest.mark.parametrize("year", ALL_YEARS)
@pytest.mark.parametrize("status", STATUSES)
def test_part_d_uses_part_b_thresholds(status, year):
    part_b = schedule("part_b", status, year)
    part_d = schedule("part_d", status, year)
    assert list(part_d.thresholds) == list(part_b.thresholds)


@pytest.mark.parametrize("year", PUBLISHED_YEARS)
@pytest.mark.parametrize("part", PARTS)
def test_joint_thresholds_double_the_individual_ones(part, year):
    # Thresholds are "more than $X" amounts stored as X + 1, except the
    # 85 percent tier's "at least $X", stored as X.
    single, joint = schedule(part, "single", year), schedule(part, "joint", year)
    assert list(joint.amounts) == list(single.amounts)
    for tier, (s, j) in enumerate(zip(single.thresholds[1:], joint.thresholds[1:])):
        if not math.isfinite(s):
            assert not math.isfinite(j)
        elif tier == 4:
            assert j == 1.5 * s
        else:
            assert j - 1 == 2 * (s - 1)


def separate_from_single(part, year, magi):
    single = schedule(part, "single", year)
    threshold_amount = single.thresholds[1] - 1
    return np.where(magi > threshold_amount, single.calc(magi + threshold_amount), 0)


@pytest.mark.parametrize("year", PUBLISHED_YEARS)
@pytest.mark.parametrize("part", PARTS)
def test_separate_schedule_at_every_boundary(part, year):
    single = schedule(part, "single", year)
    separate = schedule(part, "separate", year)
    threshold_amount = single.thresholds[1] - 1
    edges = [threshold_amount] + [
        t - threshold_amount
        for t in list(single.thresholds[2:]) + list(separate.thresholds[1:])
        if math.isfinite(t)
    ]
    magi = np.array(
        sorted({e + offset for e in edges for offset in (-1, 0, 1) if e + offset >= 0}),
        dtype=float,
    )
    np.testing.assert_array_equal(
        separate.calc(magi), separate_from_single(part, year, magi)
    )


@given(
    year=st.sampled_from(PUBLISHED_YEARS),
    part=st.sampled_from(PARTS),
    magi=st.integers(min_value=0, max_value=2_000_000),
)
def test_separate_schedule_follows_the_single_schedule(year, part, magi):
    magi = np.array([magi], dtype=float)
    separate = schedule(part, "separate", year)
    np.testing.assert_array_equal(
        separate.calc(magi), separate_from_single(part, year, magi)
    )


@pytest.mark.parametrize("year", PUBLISHED_YEARS)
@pytest.mark.parametrize("status", STATUSES)
def test_part_b_adjustments_scale_the_standard_premium(status, year):
    standard = MEDICARE.part_b.base_premium(f"{year}-01-01")
    scale = schedule("part_b", status, year)
    # The separate schedule skips tiers; match its amounts to the single
    # schedule's tiers instead of numbering them from the bottom.
    single_tiers = dict(
        (amount, percentage)
        for percentage, amount in reachable_tiers(schedule("part_b", "single", year))
    )
    for amount in scale.amounts[1:]:
        percentage = single_tiers[amount]
        expected = (percentage - 25) / 25 * standard
        assert abs(amount - expected) <= PART_B_TOLERANCE, (percentage, amount)


@pytest.mark.parametrize("year", PUBLISHED_YEARS)
def test_part_d_adjustments_are_in_proportion(year):
    tiers = reachable_tiers(schedule("part_d", "single", year))
    top_percentage, top_amount = tiers[-1]
    for percentage, amount in tiers:
        expected = (percentage - 25.5) / (top_percentage - 25.5) * top_amount
        assert abs(amount - expected) <= PART_D_TOLERANCE, (percentage, amount)


@pytest.mark.parametrize("year", range(FIRST_MODELED_YEAR, 2019))
@pytest.mark.parametrize("status", STATUSES)
@pytest.mark.parametrize("part", PARTS)
def test_no_85_percent_tier_before_2019(part, status, year):
    # The Bipartisan Budget Act of 2018 (section 53114) added the tier for
    # 2019; before then the 80 percent tier applied at any higher income.
    scale = schedule(part, status, year)
    eighty_percent = reachable_tiers(schedule(part, "single", year))[3]
    assert eighty_percent[0] == 80
    assert scale.calc(np.array([1e9]))[0] == eighty_percent[1]
    if status != "separate":
        assert not math.isfinite(scale.thresholds[-1])
