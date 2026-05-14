"""Tests for the refundable credit conversion autoloader.

YAML tests force-apply the reform via the `reforms:` directive, which
bypasses `create_refundable_credit_conversion_reform`. These tests
exercise the autoloader directly so the bypass flag and the default
inactive path are covered.
"""

from policyengine_us.reforms.refundable_credit_conversion import (
    create_refundable_credit_conversion_reform,
)
from policyengine_us.system import system


def test_autoloader_returns_none_when_in_effect_false_throughout_window():
    """Default parameters: in_effect is false for all years; autoloader returns None."""
    result = create_refundable_credit_conversion_reform(system.parameters, "2026")
    assert result is None


def test_bypass_flag_skips_lookahead_and_returns_reform():
    """bypass=True returns the reform without checking in_effect."""
    result = create_refundable_credit_conversion_reform(None, None, bypass=True)
    assert result is not None
