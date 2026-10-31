"""Runtime parameter selection for the opt-in eligibility-year PIA service."""

from decimal import Decimal

import pytest
from policyengine_core.parameters import ParameterNode

from policyengine_us import Simulation
from policyengine_us.tools.social_security.parameters import (
    bend_points_at,
    formula_path_at,
)
from policyengine_us.tools.social_security.pia import (
    FormulaPath,
    compute_pia,
    progressive_threshold,
)


@pytest.fixture(scope="module")
def reference_parameters():
    return Simulation.default_tax_benefit_system_instance.parameters


@pytest.fixture(scope="module")
def calculator_parameters(reference_parameters):
    """Keep actual processed Core parameters without cloning unrelated policy.

    These subtrees include historical bend points, projected future scales,
    null optional values and dated reform settings. New ancestor nodes keep
    the adapter's production paths intact while avoiding a whole-US tree copy
    and whole-US instant snapshots for each isolated parameter reform.
    """
    root = ParameterNode(data={})
    for path in (
        "gov.ssa.social_security.pia",
        "gov.contrib.ssa.pia",
        "gov.contrib.congress.s770",
    ):
        parts = path.split(".")
        source = reference_parameters
        destination = root
        for index, part in enumerate(parts):
            source = getattr(source, part)
            if index == len(parts) - 1:
                destination.add_child(part, source.clone())
            else:
                if part not in destination.children:
                    destination.add_child(
                        part,
                        ParameterNode(name=".".join(parts[: index + 1]), data={}),
                    )
                destination = destination.children[part]
    return root


@pytest.fixture
def parameters(calculator_parameters):
    # Each mutable case receives its own small Core tree and empty caches.
    return calculator_parameters.clone()


def _set(parameter, value, start="2026-01-01"):
    parameter.update(start=start, value=value)


def _calculate(parameters, aime, eligibility_year, payment_year):
    path, mode = formula_path_at(parameters, eligibility_year, payment_year)
    return compute_pia(
        aime,
        eligibility_year,
        path,
        payment_year,
        mode,
        bend_points=bend_points_at(parameters, eligibility_year),
    )


def test_runtime_parameters_are_neutral_by_default(reference_parameters):
    parameters = reference_parameters
    path, mode = formula_path_at(parameters, 2020, 2026)
    assert mode == "cohort"
    assert path.s770 is False
    assert path.factor_values is None
    assert path.bend_point_multipliers == (1, 1)
    assert _calculate(parameters, 5000, 2020, 2026) == Decimal("2156.8")


def test_historical_1983_bends_are_distinct_from_modern_scale(reference_parameters):
    parameters = reference_parameters
    assert bend_points_at(parameters, 1983) == (254, 1528)
    assert _calculate(parameters, 1001, 1983, 2026) == Decimal("467.6")
    with pytest.raises(ValueError, match="before 1983"):
        bend_points_at(parameters, 1982)


def test_future_2059_bends_use_existing_uprated_scale(reference_parameters):
    parameters = reference_parameters
    bends = bend_points_at(parameters, 2059)
    scale = parameters.gov.ssa.social_security.pia("2059-01-01").formula_factors
    assert bends == tuple(scale.thresholds[1:3])
    assert bends[0] > bend_points_at(parameters, 2026)[0]
    assert 0 < bends[0] < bends[1]


def test_custom_factor_schedule_is_selected_by_eligibility(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.factors.third, 0.05, "2027-01-01")
    _set(p.factors.start_year, 2027)
    path_2026, mode = formula_path_at(parameters, 2026, 2030)
    path_2027, _ = formula_path_at(parameters, 2027, 2030)
    assert mode == "cohort"
    assert path_2026.factor_values is None
    assert path_2027.factor_values == (0.9, 0.32, 0.05)
    assert _calculate(parameters, 10000, 2026, 2030) == compute_pia(
        10000, 2026, bend_points=bend_points_at(parameters, 2026)
    )


def test_cohort_master_start_does_not_reach_older_cohort_without_recompute(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.factors.first, 0.95, "1983-01-01")
    _set(p.in_effect, True, "2026-01-01")
    path, mode = formula_path_at(parameters, 2020, 2035)
    assert mode == "cohort"
    assert path.factor_values is None
    assert _calculate(parameters, 5000, 2020, 2035) == Decimal("2156.8")


def test_cohort_master_later_off_preserves_previously_eligible_cohort_path(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True, "2026-01-01")
    _set(p.in_effect, False, "2030-01-01")
    _set(p.factors.first, 0.95, "2026-01-01")
    initial, initial_mode = formula_path_at(parameters, 2027, 2027)
    later, later_mode = formula_path_at(parameters, 2027, 2035)
    assert later_mode == initial_mode == "cohort"
    assert later == initial
    assert later.factor_values == (0.95, 0.32, 0.15)
    assert _calculate(parameters, 5000, 2027, 2035) == _calculate(
        parameters, 5000, 2027, 2027
    )


def test_explicit_custom_recompute_uses_payment_formula_and_initial_bends(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.recompute_existing, True)
    _set(p.factors.third, 0.05, "2027-01-01")
    _set(p.factors.start_year, 2027)
    path, mode = formula_path_at(parameters, 2020, 2027)
    assert mode == "retroactive"
    assert path.factor_values == (0.9, 0.32, 0.05)
    assert _calculate(parameters, 7000, 2020, 2027) == Decimal("2468.7")


def test_s770_recomputes_without_extending_custom_cohort_reform(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.effective_year, 2026)
    _set(p.bend_point_multipliers.second, 1.1)
    _set(parameters.gov.contrib.congress.s770.section_2.in_effect, True)
    path, mode = formula_path_at(parameters, 2020, 2026)
    assert mode == "retroactive"
    assert path.s770 is True
    assert path.bend_point_multipliers == (1, 1)
    assert _calculate(parameters, 5000, 2020, 2026) == Decimal("2313.6")


def test_progressive_enable_with_unset_fraction_fails_on_runtime_adapter(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.progressive_price_indexing.in_effect, True)
    with pytest.raises(ValueError, match="bend-point fraction"):
        _calculate(parameters, 5000, 2032, 2032)


def test_threshold_fraction_hand_example_at_published_2026_bends(reference_parameters):
    # SSA's 2026 bend points are $1,286 and $7,749:
    # https://www.ssa.gov/OACT/COLA/bendpoints.html
    # T = 1,286 + 0.4 * (7,749 - 1,286) = 1,286 + 2,585.20 = 3,871.20.
    bends = bend_points_at(reference_parameters, 2026)
    assert bends == (1286, 7749)
    for fraction, expected in ((0, "1286"), (0.4, "3871.2"), (1, "7749")):
        path = FormulaPath(bend_point_fraction=fraction)
        assert progressive_threshold(2026, path, bend_points=bends) == Decimal(expected)


@pytest.mark.parametrize("fraction", [0, 0.4, 1])
def test_runtime_threshold_reads_each_cohorts_bend_points(parameters, fraction):
    """M8: T(E) = BP1(E) + f * (BP2(E) - BP1(E)), rising as the bends do.

    The fractions are illustrative and make no claim about any percentile.
    """
    p = parameters.gov.contrib.ssa.pia
    progressive = p.progressive_price_indexing
    _set(p.in_effect, True, "2032-01-01")
    _set(progressive.in_effect, True, "2032-01-01")
    _set(progressive.bend_point_fraction, fraction, "2032-01-01")
    previous = None
    for year in range(2032, 2041):
        bends = bend_points_at(parameters, year)
        path, _ = formula_path_at(parameters, year, year)
        threshold = progressive_threshold(year, path, bend_points=bends)
        first, second = (Decimal(str(bend)) for bend in bends)
        assert threshold == first + Decimal(str(fraction)) * (second - first)
        if previous is not None:
            # Each cohort's projected bends exceed the previous cohort's, so
            # the threshold between them rises too.
            assert first > previous[1] and second > previous[2]
            assert threshold > previous[0]
        previous = threshold, first, second


def test_runtime_progressive_dollar_path_overrides_fraction(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    progressive = p.progressive_price_indexing
    _set(progressive.in_effect, True)
    _set(progressive.bend_point_fraction, 0.4)
    _set(progressive.threshold, 3500, "2032-01-01")
    path, _ = formula_path_at(parameters, 2032, 2032)
    assert (
        progressive_threshold(2032, path, bend_points=bend_points_at(parameters, 2032))
        == 3500
    )


def test_progressive_recompute_uses_selected_fraction_and_original_bends(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True, "2032-01-01")
    _set(p.recompute_existing, True, "2032-01-01")
    progressive = p.progressive_price_indexing
    _set(progressive.in_effect, True, "2032-01-01")
    _set(progressive.bend_point_fraction, 0.4, "2032-01-01")
    # Frozen benchmark inputs explicitly describe the older eligibility cohort.
    _set(progressive.maximum_aime, 10000, "2020-01-01")
    _set(progressive.maximum_pia_target, 2800, "2020-01-01")
    path, mode = formula_path_at(parameters, 2020, 2032)
    assert mode == "retroactive"
    assert path.bend_point_fraction == 0.4
    assert path.maximum_aime_by_year == {2020: 10000}
    assert progressive_threshold(2020, path, bend_points=(960, 5785)) == 2890
    assert _calculate(parameters, 10000, 2020, 2032) == 2800


@pytest.mark.parametrize("fraction", [0, 0.3, 0.6])
def test_maximum_pia_tracks_a_cpi_w_target_in_every_cohort(
    parameters, reference_parameters, fraction
):
    """Each cohort's maximum-AIME PIA equals its frozen CPI-W-grown target.

    An illustrative path: each cohort's maximum-career AIME is 1.5 times its
    second bend point, and the target grows the 2031 cohort's current-law
    maximum PIA with `gov.ssa.uprating`, the CPI-W index the model uses for
    COLAs (with its projected values). Successive cohorts' maximum PIAs
    therefore grow with that index. No value is a claim about any percentile
    or maximum-taxable career.
    """
    p = parameters.gov.contrib.ssa.pia
    progressive = p.progressive_price_indexing
    _set(p.in_effect, True, "2032-01-01")
    _set(progressive.in_effect, True, "2032-01-01")
    _set(progressive.bend_point_fraction, fraction, "2032-01-01")
    cpi_w = reference_parameters.gov.ssa.uprating
    anchor_bends = bend_points_at(parameters, 2031)
    anchor = compute_pia(
        1.5 * anchor_bends[1], 2031, bend_points=anchor_bends, round_result=False
    )
    cohorts = {}
    for year in range(2032, 2041):
        maximum = 1.5 * bend_points_at(parameters, year)[1]
        target = round(float(anchor) * cpi_w(f"{year}-01-01") / cpi_w("2031-01-01"), 2)
        _set(progressive.maximum_aime, maximum, f"{year}-01-01")
        _set(progressive.maximum_pia_target, target, f"{year}-01-01")
        cohorts[year] = maximum, target
    previous = None
    for year, (maximum, target) in cohorts.items():
        path, mode = formula_path_at(parameters, year, year)
        assert path.maximum_pia_target_by_year == {year: target}
        result = compute_pia(
            maximum,
            year,
            path,
            year,
            mode,
            bend_points=bend_points_at(parameters, year),
            round_result=False,
        )
        assert result == Decimal(str(target))
        if previous is not None:
            assert float(result / previous) == pytest.approx(
                cpi_w(f"{year}-01-01") / cpi_w(f"{year - 1}-01-01"), rel=1e-5
            )
        previous = result


def test_full_indexing_rejects_missing_frozen_runtime_scale(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.full_price_indexing.in_effect, True)
    with pytest.raises(ValueError, match="real-wage scale"):
        _calculate(parameters, 5000, 2032, 2032)


def test_frozen_full_indexing_scale_is_read_at_eligibility_not_payment(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    _set(p.full_price_indexing.in_effect, True)
    _set(p.full_price_indexing.real_wage_scale, 1, "2032-01-01")
    _set(p.full_price_indexing.real_wage_scale, 0.9, "2033-01-01")
    path, _ = formula_path_at(parameters, 2032, 2035)
    assert path.real_wage_scale_by_year == {2032: 1}


@pytest.mark.parametrize(
    "missing_field,match",
    [
        ("real_wage_scale", "real-wage scale"),
        ("maximum_aime", "maximum-career AIME"),
        ("maximum_pia_target", "maximum-career PIA target"),
    ],
)
def test_frozen_2032_value_cannot_implicitly_serve_future_cohort(
    parameters, missing_field, match
):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    if missing_field == "real_wage_scale":
        _set(p.full_price_indexing.in_effect, True)
        _set(p.full_price_indexing.real_wage_scale, 1, "2032-01-01")
    else:
        progressive = p.progressive_price_indexing
        _set(progressive.in_effect, True)
        _set(progressive.bend_point_fraction, 0.4)
        bends = bend_points_at(parameters, 2054)
        maximum = 3 * bends[1]
        target = float(
            compute_pia(maximum, 2054, bend_points=bends, round_result=False)
        )
        for field, value in (("maximum_aime", maximum), ("maximum_pia_target", target)):
            _set(
                getattr(progressive, field),
                value,
                "2032-01-01" if field == missing_field else "2054-01-01",
            )
    with pytest.raises(ValueError, match=match):
        _calculate(parameters, 5000, 2054, 2054)


def test_frozen_dollar_override_applies_only_to_its_explicit_cohort(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    progressive = p.progressive_price_indexing
    _set(progressive.in_effect, True)
    _set(progressive.bend_point_fraction, 0.4)
    _set(progressive.threshold, 3500, "2032-01-01")
    supplied, _ = formula_path_at(parameters, 2032, 2032)
    future, _ = formula_path_at(parameters, 2054, 2054)
    assert supplied.threshold_by_year == {2032: 3500}
    assert future.threshold_by_year is None
    bends = bend_points_at(parameters, 2054)
    assert progressive_threshold(2054, future, bend_points=bends) == Decimal(
        str(bends[0])
    ) + Decimal(".4") * (Decimal(str(bends[1])) - Decimal(str(bends[0])))
    # Without the fraction, the earlier dollar observation supplies no
    # threshold for the later cohort and the affected provision fails.
    _set(progressive.bend_point_fraction, None, "2054-01-01")
    with pytest.raises(ValueError, match="bend-point fraction"):
        _calculate(parameters, 5000, 2054, 2054)
