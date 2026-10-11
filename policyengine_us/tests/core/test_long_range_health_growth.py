"""Long-range growth for CMS health spending upraters.

After a series' last projected year, ``extend_parameter_values`` with
``long_range_growth`` knots moves each year's growth linearly from the
measured short-range rate, placed at the last projected year, to the 2026
Medicare Trustees' 2050 and 2100 rates. The Trustees interpolate years 11
through 25 of their projection the same way (2026 Medicare Trustees Report,
file pages 24 and 180).

Invariants:

1. Knots: the rate in a knot year is that knot's rate exactly.
2. Betweenness: every rate lies between the two knots around it, so the path
   never overshoots either end; after the last knot the rate holds.
3. Closed form: the rate in year y between knots (y0, g0) and (y1, g1) is
   g0 + (g1 - g0)(y - y0) / (y1 - y0), and the value is the last projected
   value times the product of (1 + rate). Checked against an independent
   numpy implementation, for synthetic series and for the wired CMS series.
4. Constant knots: knots equal to the short-range rate reproduce the
   compound path V_L (1 + g)^(y - L), and no knots leave the old rule intact.
5. Monotonicity: raising any knot's rate never lowers any extended value.
6. Homogeneity: scaling the projected values by c > 0 scales every extended
   value by c, so the glide depends only on growth, not on the level.
7. Projected years are untouched, and years after the end year hold the end
   year's value.
8. Trustees consistency: starting from the Trustees' 2035 per beneficiary
   growth (Table V.D1), the Medicare per-enrollee knots reproduce the growth
   in spending per enrollee implied by the Trustees' incurred expenditure
   growth (Table V.B5) and enrollment (Table V.B3) in each long-range period,
   and the Part B and Part D knots reproduce Table II.D1's total increase net
   of beneficiary growth, within the tables' rounding.
"""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode

from policyengine_us.parameters.uprating_extensions import (
    HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    MEDICARE_LONG_RANGE_DEMOGRAPHIC_MIX,
    MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH,
    MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH,
    MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH,
    extend_parameter_values,
    long_range_growth_rate,
    with_medicare_demographic_mix,
)
from policyengine_us.system import system

END_YEAR = 2100

rates = st.floats(-0.05, 0.15, allow_nan=False, allow_infinity=False)


@st.composite
def glide_cases(draw):
    last = draw(st.integers(2020, 2060))
    knot_years = draw(
        st.lists(
            st.integers(last + 1, END_YEAR + 20), min_size=1, max_size=4, unique=True
        )
    )
    knots = {year: draw(rates) for year in knot_years}
    return last, draw(rates), knots


def _series(values):
    # A node, so Parameter.update can reach a parent.
    node = ParameterNode(
        "node",
        data={
            "series": {
                "values": {f"{year}-01-01": value for year, value in values.items()}
            }
        },
    )
    return node.series


def _extend(last, short, knots, level=100.0, end_year=END_YEAR):
    """Extend a two-point series whose last projected year grows at
    ``short``."""
    series = _series({last - 1: level, last: level * (1 + short)})
    extend_parameter_values(
        series, last, end_year, long_range_growth=knots if knots else None
    )
    return series


def _value(series, year):
    return series(f"{year}-01-01")


def _reference_path(last_value, last, short, knots, end_year=END_YEAR):
    """Independent implementation: numpy interpolation and a cumulative
    product."""
    years = np.arange(last + 1, end_year + 1)
    knot_years = [last, *sorted(knots)]
    knot_rates = [short, *(knots[year] for year in sorted(knots))]
    growth = np.interp(years, knot_years, knot_rates)
    return dict(zip(years.tolist(), last_value * np.cumprod(1 + growth)))


def _average_growth(series, start, end):
    """Average annual growth from the end of ``start - 1`` to ``end``."""
    return (_value(series, end) / _value(series, start - 1)) ** (
        1 / (end - start + 1)
    ) - 1


# 1-2. Knots and betweenness.


@given(glide_cases())
def test_rate_in_a_knot_year_is_the_knot_rate(case):
    last, short, knots = case
    for year, rate in knots.items():
        assert long_range_growth_rate(year, last, short, knots) == rate


@given(glide_cases(), st.integers(1, 80))
def test_rate_lies_between_the_surrounding_knots(case, offset):
    last, short, knots = case
    year = last + offset
    points = [(last, short), *sorted(knots.items())]
    rate = long_range_growth_rate(year, last, short, knots)
    if year >= points[-1][0]:
        assert rate == points[-1][1]
        return
    (_, before), (_, after) = next(
        (left, right)
        for left, right in zip(points, points[1:])
        if left[0] < year <= right[0]
    )
    assert min(before, after) - 1e-15 <= rate <= max(before, after) + 1e-15


@pytest.mark.parametrize("year", [2034, 2020])
def test_rate_is_undefined_up_to_the_last_projected_year(year):
    with pytest.raises(ValueError):
        long_range_growth_rate(year, 2034, 0.05, {2050: 0.04})


@pytest.mark.parametrize("knots", [{}, {2034: 0.04}, {2030: 0.04, 2050: 0.04}])
def test_knots_must_follow_the_last_projected_year(knots):
    with pytest.raises(ValueError):
        long_range_growth_rate(2040, 2034, 0.05, knots)


# 3. Closed form.


def test_rate_on_the_first_segment_matches_the_closed_form():
    # 2034 at 5%, 2050 at 3%: each year moves 2 / 16 = 0.125 point.
    for offset in range(1, 17):
        rate = long_range_growth_rate(2034 + offset, 2034, 0.05, {2050: 0.03})
        assert rate == pytest.approx(0.05 - 0.00125 * offset, abs=1e-15)


@given(glide_cases(), st.floats(1, 1e6))
@settings(max_examples=60, deadline=None)
def test_extension_matches_an_independent_implementation(case, level):
    last, short, knots = case
    series = _extend(last, short, knots, level)
    reference = _reference_path(level * (1 + short), last, short, knots)
    for year, expected in reference.items():
        assert _value(series, year) == pytest.approx(expected, rel=1e-12)


# 4. Constant knots and the old rule.


@given(st.integers(2020, 2060), rates)
@settings(max_examples=40, deadline=None)
def test_constant_knots_reproduce_compound_growth(last, short):
    glided = _extend(last, short, {2050 if last < 2050 else last + 1: short})
    compounded = _extend(last, short, None)
    for year in range(last + 1, END_YEAR + 1):
        expected = 100 * (1 + short) ** (year - last + 1)
        assert _value(glided, year) == pytest.approx(expected, rel=1e-12)
        assert _value(compounded, year) == pytest.approx(expected, rel=1e-12)


# 5. Monotonicity.


@given(glide_cases(), st.data(), st.floats(1e-4, 0.05))
@settings(max_examples=60, deadline=None)
def test_raising_a_knot_never_lowers_a_value(case, data, increase):
    last, short, knots = case
    raised_year = data.draw(st.sampled_from(sorted(knots)))
    raised = {**knots, raised_year: knots[raised_year] + increase}
    base = _extend(last, short, knots)
    higher = _extend(last, short, raised)
    for year in range(last + 1, END_YEAR + 1):
        assert _value(higher, year) >= _value(base, year) * (1 - 1e-12)
    if raised_year <= END_YEAR:
        assert _value(higher, END_YEAR) > _value(base, END_YEAR)


# 6. Homogeneity.


@given(glide_cases(), st.floats(1e-3, 1e3))
@settings(max_examples=40, deadline=None)
def test_scaling_the_level_scales_every_value(case, scale):
    last, short, knots = case
    base = _extend(last, short, knots)
    scaled = _extend(last, short, knots, level=100 * scale)
    for year in range(last - 1, END_YEAR + 30):
        assert _value(scaled, year) == pytest.approx(
            scale * _value(base, year), rel=1e-12
        )


# 7. Projected years and the hold after the end year.


@given(glide_cases(), st.integers(1, 40))
@settings(max_examples=40, deadline=None)
def test_projected_years_hold_and_later_years_freeze(case, later):
    last, short, knots = case
    end_year = min(last + later, END_YEAR)
    series = _extend(last, short, knots, end_year=end_year)
    assert _value(series, last - 1) == 100
    assert _value(series, last) == pytest.approx(100 * (1 + short), rel=1e-15)
    for year in (end_year + 1, end_year + 25):
        assert _value(series, year) == _value(series, end_year)


# 8. Trustees consistency.

# Table V.D1 (file page 210): 2035 average percent change in per beneficiary
# costs, intermediate estimates.
TRUSTEES_2035_PER_BENEFICIARY_GROWTH = {
    "total": 0.054,
    "part_b": 0.067,
    "part_d": 0.031,
}
# Table V.B5 (file page 200): average annual growth in incurred Medicare
# expenditures.
TRUSTEES_INCURRED_EXPENDITURE_GROWTH = {
    (2036, 2050): 0.049,
    (2051, 2075): 0.043,
    (2076, 2100): 0.038,
}
# Table V.B3 (file page 196): beneficiaries with HI and/or SMI, thousands.
TRUSTEES_TOTAL_ENROLLMENT = {2035: 80_632, 2050: 85_413, 2075: 99_585, 2100: 103_133}
# Table II.D1 (file page 29): average annual percentage change in total
# incurred expenditures and in the number of beneficiaries, by Part.
TRUSTEES_COMPONENTS = {
    "part_b": {(2036, 2050): (0.056, 0.004), (2051, 2100): (0.041, 0.004)},
    "part_d": {(2036, 2050): (0.039, 0.004), (2051, 2100): (0.043, 0.004)},
}
# Every published rate is rounded to a tenth of a point. A period's implied
# per-enrollee growth carries two such roundings, and the glide's start rate
# and knots carry more; 0.1 point covers them for the long periods.
V_B5_TOLERANCE = 0.001
# Table II.D1's per-beneficiary growth nets two rounded components.
II_D1_TOLERANCE = 0.0015


def test_medicare_knots_compound_cost_growth_with_the_demographic_mix():
    assert MEDICARE_LONG_RANGE_DEMOGRAPHIC_MIX == -0.001
    assert MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH == pytest.approx(
        {2050: 1.038 * 0.999 - 1, 2100: 1.037 * 0.999 - 1}, abs=1e-15
    )
    assert with_medicare_demographic_mix({2050: 0.0}) == {2050: -0.001}
    # The mix lowers growth by about a tenth of a point in every Part.
    for knots in (
        MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH,
    ):
        for rate in knots.values():
            assert 0.035 < rate < 0.041


@pytest.mark.parametrize("period", TRUSTEES_INCURRED_EXPENDITURE_GROWTH)
def test_medicare_knots_reproduce_trustees_spending_per_enrollee(period):
    start, end = period
    enrollment_growth = (
        TRUSTEES_TOTAL_ENROLLMENT[end] / TRUSTEES_TOTAL_ENROLLMENT[start - 1]
    ) ** (1 / (end - start + 1)) - 1
    implied = (1 + TRUSTEES_INCURRED_EXPENDITURE_GROWTH[period]) / (
        1 + enrollment_growth
    ) - 1
    series = _extend(
        2035,
        TRUSTEES_2035_PER_BENEFICIARY_GROWTH["total"],
        MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH,
    )
    assert _average_growth(series, start, end) == pytest.approx(
        implied, abs=V_B5_TOLERANCE
    )


@pytest.mark.parametrize(
    "part, knots",
    [
        ("part_b", MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH),
        ("part_d", MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH),
    ],
)
def test_part_knots_reproduce_table_ii_d1(part, knots):
    series = _extend(2035, TRUSTEES_2035_PER_BENEFICIARY_GROWTH[part], knots)
    for (start, end), (total, beneficiaries) in TRUSTEES_COMPONENTS[part].items():
        implied = (1 + total) / (1 + beneficiaries) - 1
        assert _average_growth(series, start, end) == pytest.approx(
            implied, abs=II_D1_TOLERANCE
        )


def test_repeating_the_2035_rate_misses_the_trustees_path():
    """The rule this replaces: 5.4 percent a year from 2036 runs a point and
    more above every period's implied growth."""
    series = _extend(2035, TRUSTEES_2035_PER_BENEFICIARY_GROWTH["total"], None)
    for (start, end), growth in TRUSTEES_INCURRED_EXPENDITURE_GROWTH.items():
        enrollment_growth = (
            TRUSTEES_TOTAL_ENROLLMENT[end] / TRUSTEES_TOTAL_ENROLLMENT[start - 1]
        ) ** (1 / (end - start + 1)) - 1
        implied = (1 + growth) / (1 + enrollment_growth) - 1
        assert _average_growth(series, start, end) - implied > 0.009


# Wiring of the CMS series in the tax-benefit system.

PARAMETERS = system.parameters
WIRED_SERIES = [
    (PARAMETERS.calibration.gov.hhs.cms.moop_per_capita, 2035),
    (PARAMETERS.calibration.gov.hhs.cms.esi_premium_per_enrollee, 2034),
]


@pytest.mark.parametrize("parameter, last", WIRED_SERIES)
def test_cms_series_glide_to_per_capita_health_spending(parameter, last):
    short = _value(parameter, last) / _value(parameter, last - 1) - 1
    reference = _reference_path(
        _value(parameter, last),
        last,
        short,
        HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    )
    for year, expected in reference.items():
        assert _value(parameter, year) == pytest.approx(expected, rel=1e-12)
    assert _value(parameter, 2150) == _value(parameter, END_YEAR)
    # From 2050 the series grows at the Trustees' 4.3 to 4.1 percent.
    for year in (2051, 2075, END_YEAR):
        growth = _value(parameter, year) / _value(parameter, year - 1) - 1
        assert 0.041 - 1e-12 <= growth <= 0.043 + 1e-12
    assert _average_growth(parameter, 2051, END_YEAR) == pytest.approx(0.042, abs=1e-4)
