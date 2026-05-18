"""Tests for the refundable credit conversion autoloader.

YAML tests force-apply the reform via the `reforms:` directive, which
bypasses `create_refundable_credit_conversion_reform`. These tests
exercise the autoloader directly so the bypass flag, the default
inactive path, and the 5-year forward-lookahead window are all covered.
"""

import copy

from policyengine_core.periods import instant

from policyengine_us.reforms.refundable_credit_conversion import (
    create_refundable_credit_conversion_reform,
)
from policyengine_us.system import system


def _parameters_with_in_effect_year(year: int):
    """Return a deep copy of the system parameters with `in_effect` true at the given year."""
    parameters = copy.deepcopy(system.parameters)
    parameters.gov.contrib.refundable_credit_conversion.in_effect.update(
        start=instant(f"{year}-01-01"), value=True
    )
    return parameters


def test_autoloader_returns_none_when_in_effect_false_throughout_window():
    """Default parameters: in_effect is false for all years; autoloader returns None."""
    result = create_refundable_credit_conversion_reform(system.parameters, "2026")
    assert result is None


def test_autoloader_returns_reform_when_in_effect_true_at_window_start():
    """in_effect true at the simulation year itself."""
    parameters = _parameters_with_in_effect_year(2026)
    result = create_refundable_credit_conversion_reform(parameters, "2026")
    assert result is not None


def test_autoloader_returns_reform_when_in_effect_true_at_window_end():
    """in_effect true at year+4 (last year inside the 5-year window)."""
    parameters = _parameters_with_in_effect_year(2030)
    result = create_refundable_credit_conversion_reform(parameters, "2026")
    assert result is not None


def test_autoloader_returns_none_when_in_effect_only_true_past_window():
    """in_effect true at year+6 (past the 5-year window)."""
    parameters = _parameters_with_in_effect_year(2032)
    result = create_refundable_credit_conversion_reform(parameters, "2026")
    assert result is None


def test_bypass_flag_skips_lookahead_and_returns_reform():
    """bypass=True returns the reform without checking in_effect."""
    result = create_refundable_credit_conversion_reform(None, None, bypass=True)
    assert result is not None


def test_bypass_flag_overrides_in_effect_false():
    """bypass=True returns a reform even when in_effect is false everywhere."""
    result = create_refundable_credit_conversion_reform(
        system.parameters, "2026", bypass=True
    )
    assert result is not None
