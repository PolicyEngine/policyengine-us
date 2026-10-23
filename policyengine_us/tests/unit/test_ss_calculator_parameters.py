"""Runtime parameter selection for the opt-in eligibility-year PIA service."""

from decimal import Decimal

import pytest

from policyengine_us import Simulation
from policyengine_us.tools.social_security.parameters import (
    bend_points_at,
    formula_path_at,
)
from policyengine_us.tools.social_security.pia import compute_pia, progressive_threshold


@pytest.fixture(scope="module")
def reference_parameters():
    return Simulation.default_tax_benefit_system_instance.parameters


@pytest.fixture
def parameters(reference_parameters):
    # Reuse the one read-only runtime system; only reform cases copy its tree.
    return reference_parameters.clone()


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
    scale = parameters("2059-01-01").gov.ssa.social_security.pia.formula_factors
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


def test_runtime_progressive_dollar_path_overrides_fraction(parameters):
    p = parameters.gov.contrib.ssa.pia
    _set(p.in_effect, True)
    progressive = p.progressive_price_indexing
    _set(progressive.in_effect, True)
    _set(progressive.bend_point_fraction, 0.4)
    _set(progressive.threshold, 3500)
    path, _ = formula_path_at(parameters, 2032, 2032)
    assert (
        progressive_threshold(2032, path, bend_points=bend_points_at(parameters, 2032))
        == 3500
    )


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
