"""Tests for uprating factor extensions through 2100."""

import pytest
import yaml
from policyengine_us.model_api import *
from policyengine_us.parameters.gov.irs.uprating import (
    set_irs_uprating_parameter,
    get_irs_cpi,
)


def test_irs_uprating_extends_to_2100():
    """Test that IRS uprating factors extend through 2100."""
    # Create a microsimulation and get parameters
    from policyengine_us import Microsimulation
    
    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters
    
    # Apply the uprating parameter updates
    parameters = set_irs_uprating_parameter(parameters)
    
    # Check that we can get uprating values for various years
    assert parameters.gov.irs.uprating("2035-01-01") > 0
    assert parameters.gov.irs.uprating("2050-01-01") > 0
    assert parameters.gov.irs.uprating("2075-01-01") > 0
    assert parameters.gov.irs.uprating("2100-01-01") > 0
    
    # Verify growth is consistent after 2035
    uprating_2035 = parameters.gov.irs.uprating("2035-01-01")
    uprating_2036 = parameters.gov.irs.uprating("2036-01-01")
    uprating_2037 = parameters.gov.irs.uprating("2037-01-01")
    
    # Calculate growth rates and verify they're consistent
    growth_rate_1 = uprating_2036 / uprating_2035
    growth_rate_2 = uprating_2037 / uprating_2036
    
    # Growth rates should be approximately equal (within 0.1%)
    assert abs(growth_rate_1 - growth_rate_2) < 0.001


def test_snap_uprating_extends_to_2100():
    """Test that SNAP uprating factors extend through 2100."""
    # Load the SNAP uprating YAML file
    with open("policyengine_us/parameters/gov/usda/snap/uprating.yaml") as f:
        data = yaml.safe_load(f)
    
    values = data["values"]
    
    # Check that we have values for key years
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in SNAP uprating"
    
    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]
    
    # Should be significantly higher than 2034 value (391.3)
    assert value_2100 > 1600, f"2100 SNAP uprating value {value_2100} seems too low"
    
    # Check that growth is consistent
    # 2033: 382.7, 2034: 391.3 => growth rate ~1.02246
    dates_2033 = [k for k in values.keys() if k.year == 2033]
    dates_2034 = [k for k in values.keys() if k.year == 2034]
    
    if dates_2033 and dates_2034:
        value_2033 = values[dates_2033[0]]
        value_2034 = values[dates_2034[0]]
        expected_growth = value_2034 / value_2033
        
        # Check a mid-range year (2050)
        dates_2050 = [k for k in values.keys() if k.year == 2050]
        if dates_2050:
            value_2050 = values[dates_2050[0]]
            # Should be approximately 391.3 * (1.02246 ** 16)
            expected_2050 = value_2034 * (expected_growth ** 16)
            assert abs(value_2050 - expected_2050) / expected_2050 < 0.01


def test_cpi_u_extends_to_2100():
    """Test that CPI-U extends through 2100."""
    with open("policyengine_us/parameters/gov/bls/cpi/cpi_u.yaml") as f:
        data = yaml.safe_load(f)
    
    values = data["values"]
    
    # Check for 2100 values
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in CPI-U"
    
    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]
    
    # Should be significantly higher than 2035 value (398.7)
    assert value_2100 > 1700, f"2100 CPI-U value {value_2100} seems too low"
    
    # Verify growth rate consistency
    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]
    
    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034
        
        # Should be approximately 1.02336 (2.336% annual)
        assert abs(growth_rate - 1.02336) < 0.001


def test_chained_cpi_u_extends_to_2100():
    """Test that Chained CPI-U extends through 2100."""
    with open("policyengine_us/parameters/gov/bls/cpi/c_cpi_u.yaml") as f:
        data = yaml.safe_load(f)
    
    values = data["values"]
    
    # Check for 2100 values
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in Chained CPI-U"
    
    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]
    
    # Should be significantly higher than 2035 value (215.4)
    assert value_2100 > 750, f"2100 Chained CPI-U value {value_2100} seems too low"
    
    # Verify growth rate is lower than regular CPI-U (chained typically grows slower)
    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]
    
    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034
        
        # Should be approximately 1.01988 (1.988% annual)
        assert abs(growth_rate - 1.01988) < 0.001


def test_cpi_w_extends_to_2100():
    """Test that CPI-W extends through 2100."""
    with open("policyengine_us/parameters/gov/bls/cpi/cpi_w.yaml") as f:
        data = yaml.safe_load(f)
    
    values = data["values"]
    
    # Check for 2100 values
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in CPI-W"
    
    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]
    
    # Should be significantly higher than 2035 value (~396)
    assert value_2100 > 1600, f"2100 CPI-W value {value_2100} seems too low"


def test_uprating_growth_rates_are_reasonable():
    """Test that all uprating growth rates are within reasonable bounds."""
    # Annual growth rates should be between 1% and 4% for inflation measures
    MIN_ANNUAL_GROWTH = 1.01
    MAX_ANNUAL_GROWTH = 1.04
    
    # Test CPI-U growth
    with open("policyengine_us/parameters/gov/bls/cpi/cpi_u.yaml") as f:
        data = yaml.safe_load(f)
    values = data["values"]
    
    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]
    
    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034
        
        assert MIN_ANNUAL_GROWTH <= growth_rate <= MAX_ANNUAL_GROWTH, \
            f"CPI-U growth rate {growth_rate} outside reasonable bounds"
    
    # Test Chained CPI-U growth (should be lower than regular CPI-U)
    with open("policyengine_us/parameters/gov/bls/cpi/c_cpi_u.yaml") as f:
        data = yaml.safe_load(f)
    values = data["values"]
    
    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]
    
    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034
        
        assert MIN_ANNUAL_GROWTH <= growth_rate <= MAX_ANNUAL_GROWTH, \
            f"Chained CPI-U growth rate {growth_rate} outside reasonable bounds"