"""
Test TOB revenue variable with labor supply responses.
"""
import pytest
from policyengine_us import Microsimulation
from policyengine_core.reforms import Reform


def test_tob_revenue_baseline():
    """TOB revenue should be positive in baseline."""
    sim = Microsimulation()
    tob = sim.calculate("tob_revenue_total", period=2026)
    assert tob.sum() > 0


def test_tob_revenue_with_lsr():
    """TOB revenue should work with labor supply responses."""
    lsr_params = {
        "gov.simulation.labor_supply_responses.elasticities.income": {
            "2024-01-01.2100-12-31": -0.05
        }
    }
    reform = Reform.from_dict(lsr_params, country_id="us")
    sim = Microsimulation(reform=reform)

    # Should not raise RecursionError
    tob = sim.calculate("tob_revenue_total", period=2026)
    income_tax = sim.calculate("income_tax", period=2026)

    assert tob.sum() > 0
    assert income_tax.sum() > 0


if __name__ == "__main__":
    print("Testing TOB revenue...")
    test_tob_revenue_baseline()
    print("✓ Baseline works")
    test_tob_revenue_with_lsr()
    print("✓ LSR works")
    print("\n✅ All tests passed!")
