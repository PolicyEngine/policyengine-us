"""
Test Social Security taxation with parametric reforms.

These tests verify that SS taxation works correctly with:
1. Current complex threshold-based system
2. Simplified parametric reforms (e.g., flat 85% taxation)
"""

import pytest
from policyengine_us import Simulation
from policyengine_core.reforms import Reform


def test_flat_85_percent_taxation():
    """Test that flat 85% SS taxation works with zero thresholds."""
    reform_dict = {
        "gov.irs.social_security.taxability.rate.base": {
            "2026-01-01": 0.85
        },
        "gov.irs.social_security.taxability.rate.additional": {
            "2026-01-01": 0.85
        },
        "gov.irs.social_security.taxability.threshold.base.main.SINGLE": {
            "2026-01-01": 0
        },
        "gov.irs.social_security.taxability.threshold.adjusted_base.main.SINGLE": {
            "2026-01-01": 0
        }
    }

    reform = Reform.from_dict(reform_dict, country_id="us")
    sim = Simulation(
        reform=reform,
        situation={
            "people": {
                "person": {
                    "age": 70,
                    "social_security_retirement": 30_000,
                    "employment_income": 0
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "filing_status": "SINGLE"
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": "FL"
                }
            }
        }
    )

    taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)[0]
    gross_ss = sim.calculate("tax_unit_social_security", 2026)[0]

    expected = 0.85 * gross_ss
    assert abs(taxable_ss - expected) < 1, \
        f"Expected {expected:.0f} but got {taxable_ss:.0f}"


def test_flat_100_percent_taxation():
    """Test that flat 100% SS taxation works with zero thresholds."""
    reform_dict = {
        "gov.irs.social_security.taxability.rate.base": {
            "2026-01-01": 1.0
        },
        "gov.irs.social_security.taxability.rate.additional": {
            "2026-01-01": 1.0
        },
        "gov.irs.social_security.taxability.threshold.base.main.SINGLE": {
            "2026-01-01": 0
        },
        "gov.irs.social_security.taxability.threshold.adjusted_base.main.SINGLE": {
            "2026-01-01": 0
        }
    }

    reform = Reform.from_dict(reform_dict, country_id="us")
    sim = Simulation(
        reform=reform,
        situation={
            "people": {
                "person": {
                    "age": 70,
                    "social_security_retirement": 30_000,
                    "employment_income": 0
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "filing_status": "SINGLE"
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": "FL"
                }
            }
        }
    )

    taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)[0]
    gross_ss = sim.calculate("tax_unit_social_security", 2026)[0]

    assert abs(taxable_ss - gross_ss) < 1, \
        f"Expected {gross_ss:.0f} but got {taxable_ss:.0f}"


def test_standard_taxation_unchanged():
    """Ensure standard SS taxation still works correctly."""
    # Test with baseline (no reform)
    sim = Simulation(
        situation={
            "people": {
                "person": {
                    "age": 70,
                    "social_security_retirement": 30_000,
                    "employment_income": 100_000
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person"],
                    "filing_status": "SINGLE"
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": "FL"
                }
            }
        }
    )

    taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)[0]
    gross_ss = sim.calculate("tax_unit_social_security", 2026)[0]

    # For high income, should be close to 85% of benefits
    expected_pct = 0.85
    assert abs(taxable_ss - expected_pct * gross_ss) < 100, \
        f"High income should result in ~85% taxable, got {taxable_ss/gross_ss:.1%}"