"""Pure population ratio API: no simulation or parameter-tree construction."""

from decimal import Decimal
from fractions import Fraction

from hypothesis import given, settings, strategies as st
import pytest

from policyengine_us.tools.social_security.pia import (
    FormulaPath,
    compute_pia,
    inverse_pia,
)
from policyengine_us.tools.social_security.pia_ratio import compute_pia_ratio


D = Decimal
BENDS = (960, 5785)
REVIEW_PATH = FormulaPath(
    factor_values=(".95", ".32", ".15"),
    bend_point_multipliers=("1.15", 1),
)


def test_c2_exact_interval_and_gain_before_and_after_dime_truncation():
    result = compute_pia_ratio(
        "18117.12",
        2020,
        REVIEW_PATH,
        bend_points=BENDS,
        claiming_adjustment=".70",
        exact_eligibility_pia=True,
    )
    assert result.aime == result.aime_lower == D(5000)
    assert result.aime_upper == D("5000.3125")
    assert not result.measurement_uncertainty
    assert D("18117.12") * result.factor == D("19282.20")
    before_rounding = compute_pia(
        5000, 2020, REVIEW_PATH, bend_points=BENDS, round_result=False
    )
    baseline = compute_pia(5000, 2020, bend_points=BENDS, round_result=False)
    assert 12 * D(".70") * (before_rounding - baseline) == D("1165.248")


def test_c2_fra_assumption_changes_inferred_aime_and_gain():
    result = compute_pia_ratio(
        "18117.12", 2020, REVIEW_PATH, bend_points=BENDS, claiming_adjustment=1
    )
    assert result.aime == D(2978)
    assert result.measurement_uncertainty
    baseline = compute_pia(2978, 2020, bend_points=BENDS, round_result=False)
    reform = compute_pia(2978, 2020, REVIEW_PATH, bend_points=BENDS, round_result=False)
    assert 12 * (reform - baseline) == D("1664.64")
    assert (D("1664.64") / D("1165.248") - 1) == pytest.approx(D(3) / 7)


def test_s770_eighteen_percent_bend_is_distinct_from_review_fixture():
    baseline = compute_pia(5000, 2020, bend_points=BENDS, round_result=False)
    reform = compute_pia(
        5000,
        2020,
        FormulaPath(s770=True),
        2026,
        "retroactive",
        bend_points=BENDS,
        round_result=False,
    )
    assert reform - baseline == D(".1634") * BENDS[0]
    result = compute_pia_ratio(
        "18117.12",
        2020,
        FormulaPath(s770=True),
        2026,
        "retroactive",
        bend_points=BENDS,
        claiming_adjustment=".7",
        exact_eligibility_pia=True,
    )
    assert D("18117.12") * result.factor == D("19434.24")


@pytest.mark.parametrize(
    "pia", [".1", "863.9", "864", "864.1", "2407.9", "2408", "2408.1", "3000"]
)
def test_every_inverse_segment_and_boundary_uses_shared_lower_endpoint(pia):
    result = compute_pia_ratio(
        12 * D(pia), 2020, bend_points=BENDS, exact_eligibility_pia=True
    )
    interval = inverse_pia(pia, 2020, bend_points=BENDS)
    assert result.aime == interval.lower
    assert result.aime_lower == interval.lower
    assert result.aime_upper == interval.upper
    assert compute_pia(result.aime, 2020, bend_points=BENDS) == D(pia)


def test_nonterminating_lower_endpoint_is_not_rounded_down_before_forward_pia():
    result = compute_pia_ratio(
        "1.2", 2020, REVIEW_PATH, bend_points=BENDS, exact_eligibility_pia=True
    )
    assert result.factor == 1
    assert Fraction(result.aime) >= Fraction(1, 9)


def test_annual_measurement_flag_even_when_derived_pia_is_a_dime():
    result = compute_pia_ratio(
        "18117.12", 2020, bend_points=BENDS, claiming_adjustment=".7"
    )
    assert result.aime == 5000
    assert result.measurement_uncertainty


def test_annual_rounding_interval_is_propagated_through_all_divisors():
    point = compute_pia_ratio(
        "18117.12",
        2020,
        bend_points=BENDS,
        claiming_adjustment=".7",
        auxiliary_share=".5",
        cola_factor=2,
    )
    expanded = compute_pia_ratio(
        "18117.12",
        2020,
        bend_points=BENDS,
        claiming_adjustment=".7",
        auxiliary_share=".5",
        cola_factor=2,
        annual_rounding_bound=".5",
    )
    assert expanded.aime == point.aime == 5000
    assert expanded.aime_lower < point.aime_lower
    assert expanded.aime_upper > point.aime_upper
    assert expanded.measurement_uncertainty


def test_survey_non_dime_interval_does_not_claim_to_be_exact():
    result = compute_pia_ratio(
        "18117.13", 2020, bend_points=BENDS, claiming_adjustment=".7"
    )
    assert result.measurement_uncertainty
    assert result.aime == result.aime_lower > 5000
    assert result.aime_upper > result.aime
    with pytest.raises(ValueError, match="multiple of one dime"):
        compute_pia_ratio(
            "18117.13",
            2020,
            bend_points=BENDS,
            claiming_adjustment=".7",
            exact_eligibility_pia=True,
        )


def test_baseline_inverse_never_uses_reform_factors():
    lower_path = FormulaPath(factor_values=(".5", ".2", ".1"))
    for path in (REVIEW_PATH, lower_path):
        result = compute_pia_ratio(
            "25881.6", 2020, path, bend_points=BENDS, exact_eligibility_pia=True
        )
        assert result.aime == 5000


def test_custom_unreformed_historical_scale_is_used_for_both_inverse_and_pia():
    result = compute_pia_ratio(
        1200,
        2020,
        FormulaPath(factor_values=(".9", ".32", ".15")),
        bend_points=BENDS,
        factors=(".8", ".3", ".1"),
        exact_eligibility_pia=True,
    )
    assert result.aime == 125
    assert result.factor == D("1.125")


def test_colas_are_removed_before_inversion_once():
    result = compute_pia_ratio(
        "36234.24",
        2020,
        REVIEW_PATH,
        bend_points=BENDS,
        claiming_adjustment=".7",
        cola_factor=2,
        exact_eligibility_pia=True,
    )
    assert result.aime == 5000
    assert D("36234.24") * result.factor == D("38564.4")


def test_zero_benefit_returns_neutral_without_inversion_or_formula_inputs():
    result = compute_pia_ratio(0, 2020, REVIEW_PATH, bend_points=(0, 0))
    assert result.factor == 1
    assert result.aime == result.aime_lower == result.aime_upper == 0
    assert D(0) * result.factor == 0
    assert not result.measurement_uncertainty


def test_pre1983_record_is_flagged_and_left_unreformed_without_inversion():
    result = compute_pia_ratio(20000, 1982, REVIEW_PATH, bend_points=(0, 0))
    assert result.factor == 1
    assert result.pre1983
    assert result.aime == result.aime_lower == result.aime_upper == 0


@pytest.mark.parametrize("benefit", [-1, "NaN", "Infinity", True])
def test_invalid_reported_benefit_is_rejected_even_before_1983(benefit):
    with pytest.raises(ValueError, match="annual reported benefit"):
        compute_pia_ratio(benefit, 1982, bend_points=BENDS)


@pytest.mark.parametrize(
    "name", ["claiming_adjustment", "auxiliary_share", "cola_factor"]
)
@pytest.mark.parametrize("value", [0, -1, "NaN", "Infinity"])
def test_invalid_divisor_is_rejected(name, value):
    with pytest.raises(ValueError, match="positive|finite"):
        compute_pia_ratio(10000, 2020, bend_points=BENDS, **{name: value})


def test_nonpositive_baseline_pia_is_not_an_infinite_factor():
    with pytest.raises(ValueError, match="baseline PIA must be positive"):
        compute_pia_ratio(".01", 2020, REVIEW_PATH, bend_points=BENDS)


@pytest.mark.parametrize("bound", [-1, "NaN", "Infinity"])
def test_invalid_measurement_bound_rejected(bound):
    with pytest.raises(ValueError, match="annual rounding bound"):
        compute_pia_ratio(10000, 2020, bend_points=BENDS, annual_rounding_bound=bound)


def test_exact_pia_cannot_also_have_an_annual_measurement_interval():
    with pytest.raises(ValueError, match="cannot have an annual rounding bound"):
        compute_pia_ratio(
            1200,
            2020,
            bend_points=BENDS,
            exact_eligibility_pia=True,
            annual_rounding_bound=1,
        )


def test_cohort_and_shared_retroactive_modes_have_distinct_applicability():
    path = FormulaPath(factor_values=(".95", ".32", ".15"), factor_start_year=2027)
    assert compute_pia_ratio("25881.6", 2020, path, 2027, bend_points=BENDS).factor == 1
    assert (
        compute_pia_ratio(
            "25881.6", 2020, path, 2026, "retroactive", bend_points=BENDS
        ).factor
        == 1
    )
    assert (
        compute_pia_ratio(
            "25881.6", 2020, path, 2027, "retroactive", bend_points=BENDS
        ).factor
        > 1
    )


# These properties check arithmetic, not elapsed time on a shared test host.
@settings(deadline=None)
@given(
    st.decimals(min_value=".01", max_value="1000000", places=2), st.integers(1983, 2035)
)
def test_every_reform_off_is_exactly_one(benefit, year):
    assert compute_pia_ratio(benefit, year, bend_points=BENDS).factor == D(1)


@settings(deadline=None)
@given(st.integers(1, 50000))
def test_baseline_inverse_roundtrips_and_contains_the_original_aime(aime):
    pia = compute_pia(aime, 2020, bend_points=BENDS)
    result = compute_pia_ratio(
        12 * pia, 2020, bend_points=BENDS, exact_eligibility_pia=True
    )
    assert result.aime_lower <= aime < result.aime_upper
    assert compute_pia(result.aime, 2020, bend_points=BENDS) == pia


@settings(deadline=None)
@given(st.integers(1, 50000))
def test_everywhere_higher_scale_has_factor_at_least_one(aime):
    pia = compute_pia(aime, 2020, bend_points=BENDS)
    result = compute_pia_ratio(
        12 * pia, 2020, REVIEW_PATH, bend_points=BENDS, exact_eligibility_pia=True
    )
    assert result.factor >= 1


@settings(deadline=None)
@given(st.integers(1, 50000), st.integers(0, 100))
def test_factor_is_never_negative_for_nonnegative_reform_scale(aime, percent):
    pia = compute_pia(aime, 2020, bend_points=BENDS)
    path = FormulaPath(factor_values=(Fraction(percent, 100), ".32", ".15"))
    result = compute_pia_ratio(
        12 * pia, 2020, path, bend_points=BENDS, exact_eligibility_pia=True
    )
    assert result.factor >= 0


@settings(deadline=None)
@given(st.integers(1983, 2035))
def test_zero_remains_zero_under_an_active_reform(year):
    result = compute_pia_ratio(0, year, REVIEW_PATH, bend_points=BENDS)
    assert result.factor == 1
    assert 0 * result.factor == 0
