"""Historical statutory rounding arithmetic; no model construction required."""

from decimal import Decimal
from pathlib import Path

import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.parameters.helpers import load_parameter_file

from policyengine_us.tools.ssa_cola_history import (
    apply_cola_to_pia,
    validate_cola_rounding_rule,
)


def test_history_preserves_effective_dates_payment_timing_and_correction():
    history_path = (
        Path(__file__).resolve().parents[2] / "parameters/gov/ssa/cola_history"
    )
    history = ParameterNode("cola_history", directory_path=str(history_path))
    events = {event.instant_str: event.value for event in history.rate.values_list}

    assert len(events) == 51
    assert min(events) == "1975-06-01"
    assert max(events) == "2025-12-01"
    assert "1982-12-01" not in events
    assert "1983-06-01" not in events
    assert history("1982-06-01").effective_month == 6
    assert history("1982-06-01").first_payment_month == 7
    assert history("1983-12-01").effective_month == 12
    assert history("1983-12-01").first_payment_month == 1
    assert events["1999-12-01"] == 0.025
    assert events["2009-12-01"] == events["2010-12-01"] == 0
    assert history("1981-06-01").pia_rounding == 1
    assert history("1982-06-01").pia_rounding == 2
    for date in events:
        validate_cola_rounding_rule(history(date).pia_rounding)


def test_historical_bend_points_include_initial_and_declining_wage_years():
    bendpoint_path = (
        Path(__file__).resolve().parents[2]
        / "parameters/gov/ssa/social_security/pia/formula_factors.yaml"
    )
    scale = load_parameter_file(str(bendpoint_path), "pia_formula_factors")
    assert scale("1979-01-01").thresholds == [0, 180, 1085]
    assert scale("1983-01-01").thresholds == [0, 254, 1528]
    assert scale("2010-01-01").thresholds == [0, 761, 4586]
    assert scale("2011-01-01").thresholds == [0, 749, 4517]
    assert scale("2014-01-01").thresholds == [0, 816, 4917]


def test_poms_historical_cola_rounding_sequence():
    # POMS RS 00605.021 C: June 1979, 1980, 1981 round up; June 1982 down.
    pia = Decimal("322.70")
    for rate, rule, expected in (
        ("0.099", 1, "354.70"),
        ("0.143", 1, "405.50"),
        ("0.112", 1, "451.00"),
        ("0.074", 2, "484.30"),
    ):
        pia = apply_cola_to_pia(pia, rate, rule)
        assert pia == Decimal(expected)


def test_ssa_modern_cola_rounding_example():
    # SSA's application-of-COLA example: 2,197.50 increased by 3.6 percent.
    assert apply_cola_to_pia("2197.50", "0.036", 2) == Decimal("2276.60")


@pytest.mark.parametrize("rule", [1, 2])
def test_exact_dime_is_unchanged(rule):
    assert apply_cola_to_pia("100.10", 0, rule) == Decimal("100.1")
    assert apply_cola_to_pia(0, "0.028", rule) == Decimal("0.0")


@pytest.mark.parametrize("rule", [0, 3, None, "down_to_dime", True])
def test_unknown_historical_rounding_rule_is_rejected(rule):
    with pytest.raises(ValueError, match="Unsupported historical COLA rounding rule"):
        validate_cola_rounding_rule(rule)
    with pytest.raises(ValueError, match="Unsupported historical COLA rounding rule"):
        apply_cola_to_pia(100, "0.028", rule)


@pytest.mark.parametrize(
    "pia, rate", [(-1, 0), (100, -0.01), ("NaN", 0), (100, "Infinity")]
)
def test_invalid_cola_inputs_are_rejected(pia, rate):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        apply_cola_to_pia(pia, rate, 2)
