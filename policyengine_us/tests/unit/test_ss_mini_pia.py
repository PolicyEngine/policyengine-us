"""Exact annual mini-PIA aggregation and retired-worker cohort selection.

These exercise a pure history service rather than authored model variables;
YAML cannot assert its rational intermediates or supplied formula paths.
"""

from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from hypothesis import HealthCheck, given, settings, strategies as st
from policyengine_core.parameters import ParameterNode
import pytest

import policyengine_us
from policyengine_us.tools.social_security.mini_pia import (
    blend_mini_pia,
    compute_mini_pia,
    mini_pia_share_at,
)
from policyengine_us.tools.social_security.pia import FormulaPath, compute_pia


BENDS = (1000, 6000)


def _parameters():
    # Read only this small subtree, without constructing or copying a US model.
    root = ParameterNode(data={})
    parent = root
    for name in ("gov", "contrib", "ssa", "history"):
        child = ParameterNode(name, data={})
        parent.add_child(name, child)
        parent = child
    path = (
        Path(policyengine_us.__file__).resolve().parent
        / "parameters/gov/contrib/ssa/history/mini_pia"
    )
    parent.add_child("mini_pia", ParameterNode("mini_pia", directory_path=str(path)))
    return root


def test_hand_computed_mini_pias_and_fixed_divisor():
    baseline = compute_mini_pia([60000] * 33 + [120000], 2036, bend_points=BENDS)
    owners = compute_mini_pia([60000] * 33 + [55410, 120000], 2036, bend_points=BENDS)
    assert baseline.annual_mini_pias[:33] == (Fraction(2180),) * 33
    assert baseline.annual_mini_pias[33] == 3100
    assert owners.annual_mini_pias[33] == Fraction("2057.60")
    assert baseline.mini_pia == Fraction(75040, 37)
    assert owners.mini_pia == Fraction("77097.60") / 37
    assert len(owners.selected_mini_pias) == 40
    assert owners.selected_mini_pias[-5:] == (0,) * 5
    # Combining after the blend, then truncating once, gives the fixture dime.
    combined = blend_mini_pia("2221.9", owners.mini_pia, 1) + Fraction("4.8")
    assert (combined * 10).__floor__() / 10 == 2088.5


def test_top_40_annual_pias_are_selected_instead_of_top_35():
    result = compute_mini_pia([60000] * 41 + [120000], 2036, bend_points=BENDS)
    assert result.selected_mini_pias == (Fraction(3100),) + (Fraction(2180),) * 39
    assert result.mini_pia == Fraction(3100 + 39 * 2180, 37)


def test_annual_pia_and_blend_retain_fractional_cents():
    path = FormulaPath(factor_values=(1, 1, 1))
    result = compute_mini_pia([1], 2036, bend_points=BENDS, formula_path=path)
    assert result.annual_mini_pias == (Fraction(1, 12),)
    assert result.mini_pia == Fraction(1, 444)
    assert blend_mini_pia("0.1", result.mini_pia, "0.2") == Fraction(893, 11100)


def test_empty_certified_career_pads_40_zeros():
    result = compute_mini_pia([], 2036, bend_points=BENDS)
    assert result.annual_mini_pias == ()
    assert result.selected_mini_pias == (0,) * 40
    assert result.mini_pia == 0


@pytest.mark.parametrize("year", [1982, 1979])
def test_mini_pia_rejects_benchmarks_before_1983_even_for_empty_career(year):
    with pytest.raises(ValueError, match="before 1983"):
        compute_mini_pia([], year, bend_points=BENDS)


def test_empty_career_still_validates_shared_formula():
    with pytest.raises(ValueError, match="bend points"):
        compute_mini_pia([], 2036, bend_points=(0, 6000))


def test_negative_annual_earnings_rejected():
    with pytest.raises(ValueError, match="nonnegative"):
        compute_mini_pia([-1], 2036, bend_points=BENDS)


@pytest.mark.parametrize("share", ["-0.01", "1.01"])
def test_invalid_blend_share_rejected(share):
    with pytest.raises(ValueError, match="between zero and one"):
        blend_mini_pia(2180, 2028, share)


@settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    conventional=st.integers(min_value=0, max_value=100000),
    annual=st.lists(st.integers(min_value=0, max_value=1000000), max_size=50),
)
def test_share_zero_equals_conventional_pia(conventional, annual):
    mini = compute_mini_pia(annual, 2036, bend_points=BENDS)
    assert blend_mini_pia(conventional, mini.mini_pia, 0) == conventional


def test_disability_pia_is_unchanged_at_full_retirement_share():
    assert blend_mini_pia("2180", "2028.108108", 1, disability=True) == 2180


def test_mini_uses_shared_payment_year_reform_rules():
    path = FormulaPath(factor_values=(1, 1, 1), factor_start_year=2038)
    cohort = compute_mini_pia(
        [60000], 2036, bend_points=BENDS, formula_path=path, payment_year=2039
    )
    recomputed = compute_mini_pia(
        [60000],
        2036,
        bend_points=BENDS,
        formula_path=path,
        payment_year=2039,
        recompute_mode="retroactive",
    )
    assert cohort.annual_mini_pias == (Fraction(2180),)
    assert recomputed.annual_mini_pias == (Fraction(5000),)


@pytest.mark.parametrize(
    "year,expected",
    [
        (2031, 0),
        (2032, ".2"),
        (2033, ".4"),
        (2034, ".6"),
        (2035, ".8"),
        (2036, 1),
        (2038, 1),
        (2054, 1),
    ],
)
def test_oact_2032_to_2036_phase_is_parameterized(year, expected):
    parameters = _parameters()
    assert mini_pia_share_at(parameters, year) == 0
    parameters.gov.contrib.ssa.history.mini_pia.in_effect.update(
        start="1983-01-01", value=True
    )
    assert mini_pia_share_at(parameters, year) == Fraction(expected)
    assert mini_pia_share_at(parameters, year, disability=True) == 0


def test_custom_cohort_share_changes_only_selected_years():
    parameters = _parameters()
    settings = parameters.gov.contrib.ssa.history.mini_pia
    settings.in_effect.update(start="1983-01-01", value=True)
    settings.share.update(start="2038-01-01", value=0.5)
    assert mini_pia_share_at(parameters, 2036) == 1
    assert mini_pia_share_at(parameters, 2038) == Fraction(1, 2)
    assert mini_pia_share_at(parameters, 2054) == Fraction(1, 2)


def test_shared_formula_exposes_exact_rational_only_when_requested():
    assert compute_pia(1, 2036, bend_points=BENDS) == Decimal("0.9")
    exact = compute_pia(
        Fraction(1, 12), 2036, bend_points=BENDS, round_result=False, exact_result=True
    )
    assert exact == Fraction(3, 40)
    assert isinstance(exact, Fraction)
    with pytest.raises(ValueError, match="exact_result requires"):
        compute_pia(1, 2036, bend_points=BENDS, exact_result=True)
