"""Tests for the refundable credit conversion autoloader.

YAML tests force-apply the reform via the `reforms:` directive, which
bypasses `create_refundable_credit_conversion_reform`. These tests
exercise the autoloader directly for its two cheapest properties: the
bypass flag and the default-inactive return-None path.

The 5-year forward-lookahead window itself is not unit-tested here:
constructing parameter trees with `in_effect` true at specific future
years requires a `copy.deepcopy(system.parameters)` per case, which
pushes peak memory past the CI runner cap when this directory's batch
runs (the deepcopy materializes the entire PolicyEngine parameter
tree). The lookahead logic is the same byte-for-byte pattern used by
streamlined_eitc, AWRA, ECPA, and a dozen other contrib reforms — none
of which unit-test the window directly either.
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


def test_bypass_flag_overrides_in_effect_false():
    """bypass=True returns a reform even when in_effect is false everywhere."""
    result = create_refundable_credit_conversion_reform(
        system.parameters, "2026", bypass=True
    )
    assert result is not None
