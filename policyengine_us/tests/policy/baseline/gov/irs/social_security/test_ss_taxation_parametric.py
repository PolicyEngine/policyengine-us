"""
Test Social Security taxation with parametric reforms.

These tests verify that SS taxation works correctly both with:
1. Current complex threshold-based system
2. Simplified parametric reforms (e.g., flat 85% taxation)
"""

import pytest
from policyengine_us import Simulation
from policyengine_core.reforms import Reform
import numpy as np


class TestCurrentSSFormula:
    """Tests that verify the current formula works correctly."""

    def test_no_taxation_below_threshold(self):
        """SS benefits should not be taxed if income is below thresholds."""
        sim = Simulation(
            situation={
                "people": {
                    "person": {
                        "age": 70,
                        "social_security_retirement": 15_000,
                        "employment_income": 0
                    }
                },
                "tax_units": {
                    "tax_unit": {
                        "members": ["person"]
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
        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        assert taxable_ss[0] == 0, "No SS should be taxable below threshold"

    def test_50_percent_taxation_middle_income(self):
        """SS benefits should be taxed at 50% rate for middle incomes."""
        sim = Simulation(
            situation={
                "people": {
                    "person": {
                        "age": 70,
                        "social_security_retirement": 20_000,
                        "employment_income": 20_000
                    }
                },
                "tax_units": {
                    "tax_unit": {
                        "members": ["person"]
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
        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        gross_ss = sim.calculate("tax_unit_social_security", 2026)
        # Should be taxed at 50% rate (between thresholds)
        assert 0 < taxable_ss[0] <= 0.5 * gross_ss[0]

    def test_85_percent_taxation_high_income(self):
        """SS benefits should be taxed at up to 85% for high incomes."""
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
                        "members": ["person"]
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
        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        gross_ss = sim.calculate("tax_unit_social_security", 2026)
        # Should be close to 85% for high income
        assert abs(taxable_ss[0] - 0.85 * gross_ss[0]) < 100


class TestParametricReforms:
    """Tests for parametric reforms that should work but currently don't."""

    def test_flat_85_percent_with_zero_thresholds_should_work(self):
        """
        Setting thresholds to 0 and rates to 85% should tax 85% of SS.

        This test currently FAILS and demonstrates the issue we're trying to fix.
        """
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

        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        gross_ss = sim.calculate("tax_unit_social_security", 2026)

        # This SHOULD pass but currently fails
        expected = 0.85 * gross_ss[0]
        assert abs(taxable_ss[0] - expected) < 1, \
            f"Expected {expected:.0f} but got {taxable_ss[0]:.0f}"

    def test_flat_100_percent_taxation_should_work(self):
        """
        Should be able to tax 100% of SS benefits parametrically.

        This test currently FAILS.
        """
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

        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        gross_ss = sim.calculate("tax_unit_social_security", 2026)

        # Should tax 100% of benefits
        assert abs(taxable_ss[0] - gross_ss[0]) < 1, \
            f"Expected {gross_ss[0]:.0f} but got {taxable_ss[0]:.0f}"

    def test_flat_50_percent_taxation_should_work(self):
        """
        Should be able to tax exactly 50% of SS benefits parametrically.

        This test currently FAILS.
        """
        reform_dict = {
            "gov.irs.social_security.taxability.rate.base": {
                "2026-01-01": 0.5
            },
            "gov.irs.social_security.taxability.rate.additional": {
                "2026-01-01": 0.5
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

        taxable_ss = sim.calculate("tax_unit_taxable_social_security", 2026)
        gross_ss = sim.calculate("tax_unit_social_security", 2026)

        # Should tax exactly 50% of benefits
        expected = 0.5 * gross_ss[0]
        assert abs(taxable_ss[0] - expected) < 1, \
            f"Expected {expected:.0f} but got {taxable_ss[0]:.0f}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])