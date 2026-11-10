"""Long-range growth for CMS health spending upraters.

After a series' last projected year, ``extend_parameter_values`` with
``long_range_growth`` knots moves each year's growth linearly from the
measured short-range rate, placed at the last projected year, to the 2026
Medicare Trustees' 2050 and 2100 rates. The Trustees interpolate years 11
through 25 of their projection between the short-range and long-range rates
(2026 Medicare Trustees Report, file pages 24 and 180); this path is linear.

Invariants:

1. Knots: the rate in a knot year is that knot's rate exactly.
2. Betweenness: every rate lies between the two knots around it, so the path
   never overshoots either end; after the last knot the rate holds.
3. Closed form: the rate in year y between knots (y0, g0) and (y1, g1) is
   g0 + (g1 - g0)(y - y0) / (y1 - y0), and the value is the last projected
   value times the product of (1 + rate). Checked against an independent
   numpy implementation, for synthetic series and for every wired series.
4. Constant knots: knots equal to the short-range rate reproduce the
   compound path V_L (1 + g)^(y - L), and no knots leave the old rule intact.
5. Monotonicity: raising any knot's rate never lowers any extended value.
6. Homogeneity: scaling the projected values by c > 0 scales every extended
   value by c, so the glide depends only on growth, not on the level.
7. Projected years are untouched, and years after the end year hold the end
   year's value.
8. Growth years: with growth_years=(y - 1, y), the short-range rate is
   V_y / V_(y-1) - 1, and the glide still starts from it at the last
   projected year, whatever the growth between y and that year.
9. Trustees consistency: Medicare spending per enrollee, which starts its
   glide at its 2031-2032 growth in 2034, reproduces the growth in spending
   per enrollee implied by the Trustees' incurred expenditure growth (Table
   V.B5) and enrollment (Table V.B3) in each long-range period. Starting
   from the Trustees' 2035 per beneficiary growth (Table V.D1), the Part B
   and Part D knots reproduce Table II.D1's total increase net of
   beneficiary growth. The Part B premium's glide matches II.D1's Part B
   growth per beneficiary in 2051-2100, where the per capita health
   spending knots would overshoot it.
10. Guards: long_range_growth_rate rejects any rate that would make a growth
   factor zero, negative or not finite; extend_parameter_values rejects
   growth_years other than consecutive years ending by the last projected
   year, before it changes any value; and the module's knots reject
   assignment.
"""

import ast
import inspect

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode

from policyengine_us.parameters import uprating_extensions
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
PARAMETERS = system.parameters
PER_CAPITA_COST = PARAMETERS.calibration.gov.hhs.medicare.per_capita_cost
PART_B_PREMIUM = PARAMETERS.calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee

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


# 10. Guards.

bad_rates = st.one_of(
    st.floats(max_value=-1), st.sampled_from([float("nan"), float("inf")])
)


@given(glide_cases(), bad_rates, st.booleans())
def test_rates_must_keep_every_growth_factor_positive_and_finite(
    case, bad, short_is_bad
):
    last, short, knots = case
    if short_is_bad:
        short = bad
    else:
        # The last knot, which the first extended year never reaches.
        knots = {**knots, max(knots): bad}
    with pytest.raises(ValueError):
        long_range_growth_rate(last + 1, last, short, knots)


@pytest.mark.parametrize(
    "knots",
    [
        HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
        MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH,
    ],
)
def test_importers_cannot_change_the_module_knots(knots):
    with pytest.raises(TypeError):
        knots[2050] = 0.0
    assert sorted(knots) == [2050, 2100]


@pytest.mark.parametrize("growth_years", [(2030, 2032), (2032, 2031), (2034, 2035)])
def test_growth_years_name_consecutive_projected_years(growth_years):
    series = _series(
        {year: 100.0 * 1.05 ** (year - 2030) for year in range(2030, 2035)}
    )
    with pytest.raises(ValueError):
        extend_parameter_values(series, 2034, END_YEAR, growth_years=growth_years)
    # Nothing extended: later years still read the 2034 value.
    assert _value(series, 2040) == _value(series, 2034)


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


# 8. Growth years.


def test_growth_years_set_the_rate_the_glide_starts_from():
    """2031-2032 grows 5 percent and 2033-2034 faster; the glide starts from 5
    percent at 2034 and reaches the 3 percent knot in 2050."""
    series = _series({2031: 100.0, 2032: 105.0, 2033: 112.0, 2034: 120.0})
    extend_parameter_values(
        series,
        2034,
        END_YEAR,
        growth_years=(2031, 2032),
        long_range_growth={2050: 0.03},
    )
    # Hand computed: 2035 is one sixteenth of the way from 5% to 3%, so it
    # grows 0.05 - 0.02 / 16 = 4.875%, to 120 * 1.04875 = 125.85, and 2036
    # grows 4.75%, to 125.85 * 1.0475 = 131.827875.
    assert _value(series, 2035) == pytest.approx(125.85, rel=1e-12)
    assert _value(series, 2036) == pytest.approx(131.827875, rel=1e-12)
    for year in (2051, END_YEAR):
        growth = _value(series, year) / _value(series, year - 1)
        assert growth == pytest.approx(1.03, rel=1e-12)
    projected = [_value(series, year) for year in range(2031, 2035)]
    assert projected == [100, 105, 112, 120]


@st.composite
def growth_year_cases(draw):
    """A series whose last projected year comes zero to five years after its
    growth years, with arbitrary growth in between."""
    last, _, knots = draw(glide_cases())
    later = draw(st.integers(last - 5, last))
    values = {later - 1: draw(st.floats(1, 1e6))}
    for year in range(later, last + 1):
        values[year] = values[year - 1] * (1 + draw(rates))
    return last, later, values, knots


@given(growth_year_cases())
@settings(max_examples=60, deadline=None)
def test_growth_years_extension_matches_an_independent_implementation(case):
    last, later, values, knots = case
    series = _series(values)
    extend_parameter_values(
        series,
        last,
        END_YEAR,
        growth_years=(later - 1, later),
        long_range_growth=knots,
    )
    short = values[later] / values[later - 1] - 1
    reference = _reference_path(values[last], last, short, knots)
    for year, expected in reference.items():
        assert _value(series, year) == pytest.approx(expected, rel=1e-12)


# 9. Trustees consistency.

# Table V.D1 (file page 210): 2035 average percent change in per beneficiary
# costs, intermediate estimates.
TRUSTEES_2035_PER_BENEFICIARY_GROWTH = {"part_b": 0.067, "part_d": 0.031}
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
# Table V.B5 rounds expenditure growth to a tenth of a point, while Table V.B3
# gives enrollment in thousands, so a period's implied per-enrollee growth
# carries one such rounding. The glide's start rate and rounded knots, and
# its straight line where the Trustees' path is not one, carry more; 0.1
# point covers them for the long periods.
V_B5_TOLERANCE = 0.001
# Table II.D1's per-beneficiary growth nets two components rounded to a tenth
# of a point, and the knots apply 2051-2100's demographic mix to 2036-2050 as
# well. That mix is -0.1 for Part B in both periods, but -0.2 for Part D in
# 2036-2050, so the Part D glide runs 0.09 point above II.D1 there (0.12 point
# with Table V.B3's Part D enrollment).
II_D1_TOLERANCE = 0.0015


def test_medicare_knots_compound_cost_growth_with_the_demographic_mix():
    assert MEDICARE_LONG_RANGE_DEMOGRAPHIC_MIX == -0.001
    assert MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH == pytest.approx(
        {2050: 1.038 * 0.999 - 1, 2100: 1.037 * 0.999 - 1}, abs=1e-15
    )
    assert with_medicare_demographic_mix({2050: 0.0}) == pytest.approx(
        {2050: -0.001}, abs=1e-15
    )
    # The mix lowers growth by about a tenth of a point in every Part.
    for knots in (
        MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH,
        MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH,
    ):
        for rate in knots.values():
            assert 0.035 < rate < 0.041


def _implied_spending_per_enrollee_growth(period):
    """Table V.B5's incurred expenditure growth net of Table V.B3's enrollment
    growth over a period."""
    start, end = period
    enrollment_growth = (
        TRUSTEES_TOTAL_ENROLLMENT[end] / TRUSTEES_TOTAL_ENROLLMENT[start - 1]
    ) ** (1 / (end - start + 1)) - 1
    return (1 + TRUSTEES_INCURRED_EXPENDITURE_GROWTH[period]) / (
        1 + enrollment_growth
    ) - 1


@pytest.mark.parametrize("period", TRUSTEES_INCURRED_EXPENDITURE_GROWTH)
def test_medicare_spending_per_enrollee_reproduces_the_trustees_path(period):
    """The wired series starts its glide in 2034, a year before the Trustees'
    2035, from its 2031-2032 growth of 5.43 percent rather than Table V.D1's
    5.4 percent in 2035; it misses by at most 0.05 point."""
    start, end = period
    assert _average_growth(PER_CAPITA_COST, start, end) == pytest.approx(
        _implied_spending_per_enrollee_growth(period), abs=V_B5_TOLERANCE
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


def test_repeating_the_2031_2032_rate_misses_the_trustees_path():
    """The rule this replaces: 5.43 percent a year from 2035 runs 0.9 point
    and more above every period's implied growth."""
    short = _value(PER_CAPITA_COST, 2032) / _value(PER_CAPITA_COST, 2031) - 1
    for period in TRUSTEES_INCURRED_EXPENDITURE_GROWTH:
        assert short - _implied_spending_per_enrollee_growth(period) > 0.009


def _part_b_per_beneficiary_growth(period):
    total, beneficiaries = TRUSTEES_COMPONENTS["part_b"][period]
    return (1 + total) / (1 + beneficiaries) - 1


def test_part_b_premium_glide_tracks_table_ii_d1():
    """The Secretary of Health and Human Services sets the standard premium
    to cover about 25 percent of average expenditures for beneficiaries aged
    65 and over (42 U.S.C. 1395r(a); file page 97), so the premium glides to
    the Part B knots. In 2051-2100 it grows within 0.02 point of
    Table II.D1's Part B growth per beneficiary, 3.685 percent; the per
    capita health spending knots would run 0.5 point above it. In 2036-2050
    it runs 0.16 point below II.D1's 5.18 percent: half from its start at
    the premium's 6.53 percent 2034-2035 growth, below Table V.D1's 6.7
    percent Part B growth in 2035, and half from the straight-line glide
    (test_part_knots_reproduce_table_ii_d1 starts from 6.7 percent)."""
    late = _part_b_per_beneficiary_growth((2051, 2100))
    assert _average_growth(PART_B_PREMIUM, 2051, END_YEAR) == pytest.approx(
        late, abs=0.0002
    )
    short = _value(PART_B_PREMIUM, 2035) / _value(PART_B_PREMIUM, 2034) - 1
    per_capita = _extend(2035, short, HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH)
    assert _average_growth(per_capita, 2051, END_YEAR) - late > 0.005
    early = _part_b_per_beneficiary_growth((2036, 2050))
    assert _average_growth(PART_B_PREMIUM, 2036, 2050) == pytest.approx(
        early, abs=0.002
    )


# Wiring in the tax-benefit system: (series, last projected year, growth
# years, long-range knots).

CMS = PARAMETERS.calibration.gov.hhs.cms
WIRED_SERIES = [
    (CMS.moop_per_capita, 2034, None, HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH),
    (
        CMS.esi_premium_per_enrollee,
        2034,
        None,
        HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    ),
    (
        CMS.direct_purchase_premium_per_enrollee,
        2034,
        None,
        HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    ),
    (PART_B_PREMIUM, 2035, None, MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH),
    (PER_CAPITA_COST, 2034, (2031, 2032), MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH),
]


@pytest.mark.parametrize(
    "parameter, last, growth_years, knots",
    WIRED_SERIES,
    ids=[series.name for series, *_ in WIRED_SERIES],
)
def test_wired_series_glide_to_their_long_range_rates(
    parameter, last, growth_years, knots
):
    earlier, later = growth_years or (last - 1, last)
    short = _value(parameter, later) / _value(parameter, earlier) - 1
    reference = _reference_path(_value(parameter, last), last, short, knots)
    for year, expected in reference.items():
        assert _value(parameter, year) == pytest.approx(expected, rel=1e-12)
    assert _value(parameter, 2150) == _value(parameter, END_YEAR)
    # From 2050 each year grows at a rate between the 2050 and 2100 knots.
    low, high = sorted((knots[2050], knots[2100]))
    for year in range(2051, END_YEAR + 1):
        growth = _value(parameter, year) / _value(parameter, year - 1) - 1
        assert low - 1e-12 <= growth <= high + 1e-12
    assert _average_growth(parameter, 2051, END_YEAR) == pytest.approx(
        (low + high) / 2, abs=1e-4
    )


def test_every_glided_series_is_checked_here():
    """Each series that set_all_uprating_parameters extends with
    long_range_growth appears in WIRED_SERIES, so the differential check above
    covers it."""
    tree = ast.parse(inspect.getsource(uprating_extensions))
    glided = {
        ast.unparse(call.args[0]).removeprefix("parameters.")
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and getattr(call.func, "id", None) == "extend_parameter_values"
        and any(keyword.arg == "long_range_growth" for keyword in call.keywords)
    }
    assert glided == {series.name for series, *_ in WIRED_SERIES}
