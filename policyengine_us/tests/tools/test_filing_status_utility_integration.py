"""
Integration test for select_filing_status_value utility function.
Tests the function with actual PolicyEngine US tax calculations.
"""
import numpy as np
import pytest
from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value
from policyengine_us import Microsimulation


def test_select_filing_status_value_with_simple_values():
    """Test the utility with simple parameter values."""
    # Create a small test scenario
    sim = Microsimulation(
        reform={},
        dataset="policyengine_us_testing",
    )
    
    # Get filing status for test tax units
    filing_status = sim.calculate("filing_status", 2024)
    
    # Create test parameter values like those in actual parameters
    test_values = {
        "single": 1000,
        "joint": 2000,
        "separate": 1500,
        "head_of_household": 1800,
        "surviving_spouse": 2000,
    }
    
    # Apply the utility function
    result = select_filing_status_value(filing_status, test_values)
    
    # Verify results match expected values based on filing status
    for i, fs in enumerate(filing_status):
        if fs == fs.possible_values.SINGLE:
            assert result[i] == 1000
        elif fs == fs.possible_values.JOINT:
            assert result[i] == 2000
        elif fs == fs.possible_values.SEPARATE:
            assert result[i] == 1500
        elif fs == fs.possible_values.HEAD_OF_HOUSEHOLD:
            assert result[i] == 1800
        elif fs == fs.possible_values.SURVIVING_SPOUSE:
            assert result[i] == 2000


def test_select_filing_status_value_with_calc_method():
    """Test with parameter objects that have calc methods."""
    sim = Microsimulation(
        reform={},
        dataset="policyengine_us_testing",
    )
    
    filing_status = sim.calculate("filing_status", 2024)
    taxable_income = sim.calculate("taxable_income", 2024)
    
    # Mock parameter object with calc method
    class MockRateSchedule:
        def __init__(self, base_rate):
            self.base_rate = base_rate
            
        def calc(self, income, **kwargs):
            # Simple progressive rate
            return income * self.base_rate
    
    test_values = {
        "single": MockRateSchedule(0.10),
        "joint": MockRateSchedule(0.08),
        "separate": MockRateSchedule(0.12),
        "head_of_household": MockRateSchedule(0.09),
        "surviving_spouse": MockRateSchedule(0.08),
    }
    
    result = select_filing_status_value(filing_status, test_values, taxable_income)
    
    # Verify calculations
    for i, fs in enumerate(filing_status):
        income = taxable_income[i]
        if fs == fs.possible_values.SINGLE:
            assert result[i] == income * 0.10
        elif fs == fs.possible_values.JOINT:
            assert result[i] == income * 0.08
        elif fs == fs.possible_values.SEPARATE:
            assert result[i] == income * 0.12
        elif fs == fs.possible_values.HEAD_OF_HOUSEHOLD:
            assert result[i] == income * 0.09
        elif fs == fs.possible_values.SURVIVING_SPOUSE:
            assert result[i] == income * 0.08


def test_default_to_single_value():
    """Test that missing filing statuses default to SINGLE value."""
    sim = Microsimulation(
        reform={},
        dataset="policyengine_us_testing",
    )
    
    filing_status = sim.calculate("filing_status", 2024)
    
    # Only provide single and joint values
    incomplete_values = {
        "single": 999,
        "joint": 1999,
    }
    
    result = select_filing_status_value(filing_status, incomplete_values)
    
    # All non-joint filers should get the single value
    for i, fs in enumerate(filing_status):
        if fs == fs.possible_values.JOINT:
            assert result[i] == 1999
        else:
            assert result[i] == 999  # Default to single value


def test_with_right_parameter():
    """Test passing additional kwargs like right=True."""
    sim = Microsimulation(
        reform={},
        dataset="policyengine_us_testing",
    )
    
    filing_status = sim.calculate("filing_status", 2024)
    agi = sim.calculate("adjusted_gross_income", 2024)
    
    class MockThresholdCalc:
        def __init__(self, threshold):
            self.threshold = threshold
            
        def calc(self, value, right=False, **kwargs):
            if right:
                # Return next bracket threshold
                return self.threshold + 10_000
            return self.threshold
    
    test_values = {
        "single": MockThresholdCalc(50_000),
        "joint": MockThresholdCalc(100_000),
        "head_of_household": MockThresholdCalc(75_000),
        "separate": MockThresholdCalc(50_000),
        "surviving_spouse": MockThresholdCalc(100_000),
    }
    
    # Test without right parameter
    result_normal = select_filing_status_value(filing_status, test_values, agi)
    
    # Test with right=True
    result_right = select_filing_status_value(
        filing_status, test_values, agi, right=True
    )
    
    # Verify right parameter increases thresholds by 10k
    assert np.all(result_right == result_normal + 10_000)