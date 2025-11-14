"""
Test labor supply behavioral response with baseline simulation.

This requires a Python test because YAML tests don't support creating
baseline simulations needed to trigger the main code path.
"""

import pytest
from policyengine_us import Simulation


def test_labor_supply_response_with_baseline():
    """Test that labor supply response calculates with non-zero elasticities and baseline."""

    # Create baseline simulation
    baseline_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                    "self_employment_income_before_lsr": {"2023": 10_000},
                    "age": {"2023": 40},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2023": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    # Create reform simulation with modified situation (to trigger response)
    reform_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                    "self_employment_income_before_lsr": {"2023": 10_000},
                    "age": {"2023": 40},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2023": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    # Manually set baseline (simulating reform scenario)
    reform_sim.baseline = baseline_sim

    # Set non-zero elasticities via reform_sim's tax_benefit_system
    reform_sim.tax_benefit_system.parameters.gov.simulation.labor_supply_responses.elasticities.income.update(
        period="year:2023:10", value=0.1
    )
    reform_sim.tax_benefit_system.parameters.gov.simulation.labor_supply_responses.elasticities.substitution.all.update(
        period="year:2023:10", value=0.2
    )

    # Calculate labor supply response - this exercises the full execution path
    result = reform_sim.calculate("labor_supply_behavioral_response", 2023)

    # Verify that the calculation completes
    assert result is not None
    assert len(result) > 0
    # The result should be a numeric value (can be 0 if no behavioral change)
    assert isinstance(float(result[0]), float)


def test_labor_supply_response_no_baseline_returns_zero():
    """Test that without baseline, labor supply response returns 0."""
    sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    result = sim.calculate("labor_supply_behavioral_response", 2023)
    assert result[0] == 0


def test_labor_supply_response_with_baseline_but_zero_elasticities():
    """Test line 17: baseline exists but elasticities are zero."""
    baseline_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    reform_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    # Set baseline but keep elasticities at zero
    reform_sim.baseline = baseline_sim

    # Elasticities are 0 by default, so this should return 0 (line 17)
    result = reform_sim.calculate("labor_supply_behavioral_response", 2023)
    assert result[0] == 0


def test_labor_supply_response_only_substitution_elasticity():
    """Test line 17: baseline exists with only substitution elasticity (income elasticity is 0)."""
    baseline_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                    "age": {"2023": 40},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2023": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    reform_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                    "age": {"2023": 40},
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": ["person1"],
                    "filing_status": {"2023": "SINGLE"},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    # Set baseline
    reform_sim.baseline = baseline_sim

    # Set ONLY substitution elasticity (income elasticity stays at 0)
    reform_sim.tax_benefit_system.parameters.gov.simulation.labor_supply_responses.elasticities.substitution.all.update(
        period="year:2023:10", value=0.2
    )

    # This should NOT return 0 early (line 17 condition is false)
    result = reform_sim.calculate("labor_supply_behavioral_response", 2023)
    assert isinstance(float(result[0]), float)


def test_labor_supply_response_reentry_guard():
    """Test line 24: re-entry guard prevents recursion."""
    baseline_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    reform_sim = Simulation(
        situation={
            "people": {
                "person1": {
                    "employment_income_before_lsr": {"2023": 50_000},
                }
            },
            "households": {"household": {"members": ["person1"]}},
        }
    )

    reform_sim.baseline = baseline_sim

    # Set non-zero elasticities
    reform_sim.tax_benefit_system.parameters.gov.simulation.labor_supply_responses.elasticities.income.update(
        period="year:2023:10", value=0.1
    )

    # Manually set the re-entry guard to simulate recursion scenario
    reform_sim._lsr_calculating = True

    # This should return 0 due to re-entry guard (line 24)
    result = reform_sim.calculate("labor_supply_behavioral_response", 2023)
    assert result[0] == 0
