"""Monthly shared PIA formula, reform composition and exact inverse checks."""

from decimal import Decimal
from fractions import Fraction

from hypothesis import given, settings, strategies as st
import pytest

from policyengine_us.tools.social_security.pia import (
    FormulaPath,
    compute_pia,
    has_active_reform,
    inverse_pia,
    inverse_unrounded,
    progressive_threshold,
)


D = Decimal
BENDS = (960, 5785)


@pytest.mark.parametrize(
    "aime,expected",
    [(700, "630.00"), (3000, "1606.70"), (8000, "2989.20")],
)
def test_ssa_published_2023_appendix_examples(aime, expected):
    # SSA Annual Statistical Supplement 2023, Appendix D, "Computing a PIA":
    # https://www.ssa.gov/policy/docs/statcomps/supplement/2023/apnd.html
    # The last example has an unrounded PIA of $2,989.27.
    assert compute_pia(aime, 2023, bend_points=(1115, 6721)) == D(expected)


def test_review_fixture_is_distinct_from_s770():
    path = FormulaPath(
        factor_values=(".95", ".32", ".15"),
        bend_point_multipliers=("1.15", 1),
    )
    assert compute_pia(5000, 2020, bend_points=BENDS) == D("2156.8")
    assert compute_pia(5000, 2020, path, bend_points=BENDS) == D("2295.5")
    assert compute_pia(5000, 2020, path, bend_points=BENDS, round_result=False) == D(
        "2295.52"
    )


def test_supplied_pia_interval_and_lower_point_convention():
    interval = inverse_pia("2156.8", 2020, bend_points=BENDS)
    assert interval.lower == D("5000")
    assert interval.upper == D("5000.3125")
    assert interval.exact_lower == 5000
    assert interval.exact_upper == Fraction(80005, 16)
    assert compute_pia(interval.lower, 2020, bend_points=BENDS) == D("2156.8")
    assert compute_pia(interval.exact_upper, 2020, bend_points=BENDS) == D("2156.9")


@pytest.mark.parametrize("pia", ["0", ".1", "864", "1000", "2408", "3000"])
def test_inverse_at_zero_each_segment_and_bend_boundary(pia):
    interval = inverse_pia(pia, 2020, bend_points=BENDS)
    assert compute_pia(interval.exact_lower, 2020, bend_points=BENDS) == D(pia)
    assert compute_pia(interval.lower, 2020, bend_points=BENDS) == D(pia)
    assert compute_pia(interval.exact_upper, 2020, bend_points=BENDS) == D(pia) + D(
        ".1"
    )
    assert interval.exact_lower < interval.exact_upper


def test_inverse_exposes_exact_rational_nonterminating_endpoints():
    interval = inverse_pia("0.1", 2020, bend_points=BENDS)
    assert interval.exact_lower == Fraction(1, 9)
    assert interval.exact_upper == Fraction(2, 9)
    assert Fraction(interval.lower) >= interval.exact_lower
    assert inverse_unrounded(".1", 2020, bend_points=BENDS) == Fraction(1, 9)


@pytest.mark.parametrize("year", [1979, 1982])
def test_pre1983_benchmark_rejected_for_computation_and_inverse(year):
    # POMS RS 00605.021 B.2.b requires upward rounding before 1983.
    # https://secure.ssa.gov/poms.nsf/lnx/0300605021
    with pytest.raises(ValueError, match="before 1983"):
        compute_pia(1000, year, bend_points=BENDS)
    with pytest.raises(ValueError, match="before 1983"):
        inverse_pia(100, year, bend_points=BENDS)


def test_first_supported_benchmark_uses_lower_dime():
    assert compute_pia(1001, 1983, bend_points=(254, 1528)) == D("467.6")


def test_custom_factor_changes_only_from_selected_cohort():
    path = FormulaPath(factor_values=(".90", ".32", ".05"), factor_start_year=2027)
    assert compute_pia(7000, 2026, path, bend_points=BENDS) == compute_pia(
        7000, 2026, bend_points=BENDS
    )
    assert compute_pia(7000, 2027, path, bend_points=BENDS) == D("2468.7")


def test_custom_bend_change_has_explicit_cohort_gate():
    path = FormulaPath(effective_year=2027, bend_point_multipliers=("1.15", 1))
    assert compute_pia(5000, 2026, path, bend_points=BENDS) == D("2156.8")
    assert compute_pia(5000, 2027, path, bend_points=BENDS) == D("2240.3")


def test_fixed_cohort_and_aime_ignore_scoring_year_without_recompute():
    path = FormulaPath(s770=True)
    assert compute_pia(5000, 2020, path, 2025, bend_points=BENDS) == D("2156.8")
    assert compute_pia(5000, 2020, path, 2035, bend_points=BENDS) == D("2156.8")


@pytest.mark.parametrize(
    "path",
    [
        FormulaPath(),
        FormulaPath(effective_year=2027, bend_point_multipliers=(1.1, 1)),
        FormulaPath(factor_start_year=2027, factor_values=(".95", ".32", ".15")),
        FormulaPath(factor_values=(".9", ".32", ".15")),
        FormulaPath(full_price_indexing_start_year=2032),
        FormulaPath(progressive_price_indexing_start_year=2032),
        FormulaPath(s770=True),
    ],
)
def test_inactive_or_identity_paths_do_not_require_aime_inference(path):
    assert not has_active_reform(path, 2020, 2026)


def test_recompute_activation_matches_formula_applicability():
    path = FormulaPath(factor_start_year=2027, factor_values=(".9", ".32", ".05"))
    assert not has_active_reform(path, 2020, 2026, "retroactive")
    assert has_active_reform(path, 2020, 2027, "retroactive")
    assert has_active_reform(FormulaPath(s770=True), 2020, 2026, "retroactive")
    assert has_active_reform(FormulaPath(full_price_indexing_start_year=2032), 2032)


def test_s770_recomputes_old_cohort_at_original_bends_from_2026():
    # Introduced S.770 section 2: 95% first factor, 18% first-bend increase,
    # effective January 2026, with recomputation at initial-eligibility bends.
    # https://www.congress.gov/bill/119th-congress/senate-bill/770/text
    path = FormulaPath(s770=True)
    assert compute_pia(5000, 2020, path, 2025, "retroactive", bend_points=BENDS) == D(
        "2156.8"
    )
    assert compute_pia(5000, 2020, path, 2026, "retroactive", bend_points=BENDS) == D(
        "2313.6"
    )
    assert compute_pia(
        5000, 2020, path, 2026, "retroactive", bend_points=BENDS, round_result=False
    ) == D("2313.664")


@pytest.mark.parametrize("increase,expected_gain", [(False, ".05"), (True, ".1634")])
def test_s770_survivor_flag_controls_only_bend_increase(increase, expected_gain):
    path = FormulaPath(s770=True, s770_increase_first_bend_point=increase)
    baseline = compute_pia(5000, 2020, bend_points=BENDS, round_result=False)
    reform = compute_pia(
        5000, 2020, path, 2026, "retroactive", bend_points=BENDS, round_result=False
    )
    assert reform - baseline == D(expected_gain) * BENDS[0]


def test_full_price_indexing_anchor_and_all_factor_reduction():
    path = FormulaPath(
        full_price_indexing_start_year=2032,
        real_wage_scale_by_year={2032: 1, 2033: ".98"},
    )
    assert compute_pia(5000, 2031, path, bend_points=BENDS) == D("2156.8")
    assert compute_pia(5000, 2032, path, bend_points=BENDS) == D("2156.8")
    assert compute_pia(5000, 2033, path, bend_points=BENDS) == D("2113.6")
    assert compute_pia(5000, 2033, path, bend_points=BENDS, round_result=False) == D(
        "2113.664"
    )


@pytest.mark.parametrize("fraction,expected", [(0, 1000), (1, 6000), (".4", 3000)])
def test_progressive_threshold_fraction_endpoints_and_hand_example(fraction, expected):
    path = FormulaPath(bend_point_fraction=fraction)
    assert progressive_threshold(2032, path, bend_points=(1000, 6000)) == expected


def test_progressive_threshold_grows_with_eligibility_bends():
    path = FormulaPath(bend_point_fraction=".4")
    early = progressive_threshold(2032, path, bend_points=(1000, 6000))
    later = progressive_threshold(2033, path, bend_points=(1100, 6600))
    assert early == 3000
    assert later == 3300


def test_progressive_dollar_path_overrides_fraction():
    path = FormulaPath(bend_point_fraction=".4", threshold_by_year={2032: 3500})
    assert progressive_threshold(2032, path, bend_points=(1000, 6000)) == 3500


def _progressive_path(**overrides):
    values = dict(
        progressive_price_indexing_start_year=2032,
        bend_point_fraction=".4",
        maximum_aime_by_year={2032: 10000},
        maximum_pia_target_by_year={2032: 2800},
    )
    values.update(overrides)
    return FormulaPath(**values)


@pytest.mark.parametrize("aime", [0, 500, 1000, 2999, 3000])
def test_progressive_indexing_protects_every_amount_below_threshold(aime):
    assert compute_pia(aime, 2032, _progressive_path(), bend_points=(1000, 6000)) == (
        compute_pia(aime, 2032, bend_points=(1000, 6000))
    )


def test_progressive_indexing_continuity_and_maximum_target():
    path = _progressive_path()
    # F(3000)=1540; F(10000)=3100; k=(2800-1540)/(3100-1540)=21/26.
    assert (
        compute_pia(3000, 2032, path, bend_points=(1000, 6000), round_result=False)
        == 1540
    )
    assert compute_pia(10000, 2032, path, bend_points=(1000, 6000)) == 2800
    assert compute_pia(6000, 2032, path, bend_points=(1000, 6000)) == D("2315.3")


def test_progressive_fraction_preserves_exact_dime_boundaries():
    # q=13000/3, F(q)=5900/3 and k=25/34, so at AIME=5988 the
    # reformed PIA is exactly (4*5988+16100)/17 = 2356. Converting
    # q to a finite Decimal before computing k can lose one dime.
    path = _progressive_path(bend_point_fraction=Fraction(2, 3))
    assert compute_pia(5988, 2032, path, bend_points=(1000, 6000)) == 2356


def test_progressive_no_change_anchor_has_unit_above_threshold_multiplier():
    path = _progressive_path(maximum_pia_target_by_year={2032: 3100})
    for aime in (0, 1000, 3000, 6000, 10000, 12000):
        assert compute_pia(aime, 2032, path, bend_points=(1000, 6000)) == compute_pia(
            aime, 2032, bend_points=(1000, 6000)
        )


def _scale(aime, bend_points):
    # Independent unreformed formula in exact rational arithmetic.
    first, second = bend_points
    return (
        Fraction(9, 10) * min(aime, first)
        + Fraction(32, 100) * max(min(aime, second) - first, 0)
        + Fraction(15, 100) * max(aime - second, 0)
    )


@settings(deadline=None)
@given(
    st.lists(st.integers(0, 50), min_size=9, max_size=9),
    st.lists(st.integers(0, 15), min_size=9, max_size=9),
    st.fractions(min_value=0, max_value=1, max_denominator=1000),
)
def test_maximum_pia_tracks_a_price_grown_target_in_every_cohort(
    wage_growth, real_wage_gap, fraction
):
    """The maximum-AIME PIA equals each cohort's price-grown target exactly.

    Bend points and the maximum-career AIME grow with wages from the 2031
    cohort; the target grows with prices from 2031's current-law maximum PIA.
    Prices grow at most as fast as wages, keeping the target in its bounds.
    Successive cohorts' maximum PIAs therefore grow with prices.
    """
    bends, maximum = (Fraction(1542), Fraction(9294)), Fraction(14000)
    target = _scale(maximum, bends)
    wages = {}
    targets = {}
    for offset, (wage, gap) in enumerate(zip(wage_growth, real_wage_gap)):
        year = 2032 + offset
        growth = 1 + Fraction(wage, 1000)
        bends = tuple(bend * growth for bend in bends)
        maximum *= growth
        target *= growth / (1 + Fraction(gap, 1000))
        wages[year] = bends, maximum
        targets[year] = target
    path = FormulaPath(
        progressive_price_indexing_start_year=2032,
        bend_point_fraction=fraction,
        maximum_aime_by_year={year: value[1] for year, value in wages.items()},
        maximum_pia_target_by_year=targets,
    )
    previous = None
    for year, (bends, maximum) in wages.items():
        result = compute_pia(maximum, year, path, bend_points=bends, round_result=False)
        # A 50-digit Decimal of the exact rational target.
        assert abs(Fraction(result) - targets[year]) < Fraction(1, 10**40)
        if previous is not None:
            ratio = Fraction(result) / previous
            assert abs(ratio - targets[year] / targets[year - 1]) < Fraction(1, 10**30)
        previous = Fraction(result)


def test_progressive_path_before_start_needs_no_frozen_data():
    path = FormulaPath(progressive_price_indexing_start_year=2032)
    assert compute_pia(5000, 2031, path, bend_points=BENDS) == D("2156.8")


@pytest.mark.parametrize(
    "path,match",
    [
        (FormulaPath(full_price_indexing_start_year=2032), "real-wage scale"),
        (
            FormulaPath(
                full_price_indexing_start_year=2032,
                real_wage_scale_by_year={2033: 1},
            ),
            "frozen value",
        ),
        (FormulaPath(progressive_price_indexing_start_year=2032), "fraction"),
        (_progressive_path(maximum_aime_by_year=None), "maximum-career AIME"),
        (_progressive_path(maximum_pia_target_by_year=None), "PIA target"),
        (_progressive_path(maximum_aime_by_year={2032: 3000}), "must exceed"),
        (_progressive_path(maximum_pia_target_by_year={2032: 1500}), "bounds"),
        (_progressive_path(maximum_pia_target_by_year={2032: 3200}), "bounds"),
        (_progressive_path(threshold_by_year={2032: 900}), "first segment"),
        (_progressive_path(bend_point_fraction="1.1"), "between zero and one"),
        (_progressive_path(threshold_by_year={2033: 3000}), "frozen value"),
    ],
)
def test_missing_or_inconsistent_indexing_inputs_fail_explicitly(path, match):
    with pytest.raises(ValueError, match=match):
        compute_pia(5000, 2032, path, bend_points=(1000, 6000))


@pytest.mark.parametrize("bends", [(1000, 1000), (6000, 1000), (0, 6000)])
def test_bend_point_order_is_explicit(bends):
    with pytest.raises(ValueError, match="0 < first < second"):
        compute_pia(5000, 2020, bend_points=bends)


def test_custom_bend_multiplier_cannot_reverse_thresholds():
    with pytest.raises(ValueError, match="0 < first < second"):
        compute_pia(
            5000,
            2020,
            FormulaPath(bend_point_multipliers=(10, 1)),
            bend_points=BENDS,
        )


@pytest.mark.parametrize("amount", [-1, "NaN", "Infinity", True])
def test_invalid_aime_rejected(amount):
    with pytest.raises(ValueError):
        compute_pia(amount, 2020, bend_points=BENDS)


def test_ambiguous_rounded_pia_and_nonpositive_inverse_factors_rejected():
    with pytest.raises(ValueError, match="multiple of one dime"):
        inverse_pia("100.01", 2020, bend_points=BENDS)
    with pytest.raises(ValueError, match="positive historical factors"):
        inverse_pia(100, 2020, bend_points=BENDS, factors=(".9", ".32", 0))
    with pytest.raises(ValueError, match="nonnegative"):
        inverse_pia(-100, 2020, bend_points=BENDS)


def test_recompute_requires_explicit_payment_year_and_supported_mode():
    with pytest.raises(ValueError, match="requires a payment year"):
        compute_pia(1000, 2020, recompute_mode="retroactive", bend_points=BENDS)
    with pytest.raises(ValueError, match="recompute_mode"):
        compute_pia(1000, 2020, recompute_mode="automatic", bend_points=BENDS)
    with pytest.raises(ValueError, match="precede eligibility"):
        compute_pia(1000, 2020, payment_year=2019, bend_points=BENDS)


@given(st.integers(0, 50000), st.integers(0, 50000))
@pytest.mark.parametrize(
    "path",
    [
        FormulaPath(),
        FormulaPath(bend_point_multipliers=("1.15", "1.02")),
        FormulaPath(factor_values=(".95", ".32", ".05")),
        FormulaPath(s770=True),
        FormulaPath(
            full_price_indexing_start_year=2032,
            real_wage_scale_by_year={2032: ".98"},
        ),
        _progressive_path(),
    ],
)
def test_every_formula_path_is_nondecreasing_in_aime(path, first, second):
    lower, upper = sorted((first, second))
    assert compute_pia(lower, 2032, path, bend_points=(1000, 6000)) <= compute_pia(
        upper, 2032, path, bend_points=(1000, 6000)
    )


@given(st.integers(0, 50000), st.integers(1983, 2035))
def test_no_reform_equals_current_law_at_eligibility(aime, year):
    # Independent piecewise formula, evaluated as exact rational arithmetic.
    expected = (
        Fraction(9, 10) * min(aime, 960)
        + Fraction(32, 100) * max(min(aime, 5785) - 960, 0)
        + Fraction(15, 100) * max(aime - 5785, 0)
    )
    assert (
        compute_pia(aime, year, bend_points=BENDS)
        == D((expected * 10).numerator // (expected * 10).denominator) / 10
    )


@given(st.integers(0, 50000))
def test_inverse_interval_contains_original_and_reproduces_rounded_pia(aime):
    pia = compute_pia(aime, 2020, bend_points=BENDS)
    interval = inverse_pia(pia, 2020, bend_points=BENDS)
    assert interval.exact_lower <= aime < interval.exact_upper
    assert compute_pia(interval.lower, 2020, bend_points=BENDS) == pia
