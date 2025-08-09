"""Test that CPI uprating factors extend through 2100."""

import yaml
from datetime import date


def test_cpi_u_extends_to_2100():
    """Test that CPI-U extends through 2100."""
    with open(
        "policyengine_us/parameters/gov/bls/cpi/cpi_u.yaml", encoding="utf-8"
    ) as f:
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
    with open(
        "policyengine_us/parameters/gov/bls/cpi/c_cpi_u.yaml", encoding="utf-8"
    ) as f:
        data = yaml.safe_load(f)

    values = data["values"]

    # Check for 2100 values
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in Chained CPI-U"

    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]

    # Should be significantly higher than 2035 value (215.4)
    assert (
        value_2100 > 750
    ), f"2100 Chained CPI-U value {value_2100} seems too low"

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
    with open(
        "policyengine_us/parameters/gov/bls/cpi/cpi_w.yaml", encoding="utf-8"
    ) as f:
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
    min_annual_growth = 1.01
    max_annual_growth = 1.04

    # Test CPI-U growth
    with open(
        "policyengine_us/parameters/gov/bls/cpi/cpi_u.yaml", encoding="utf-8"
    ) as f:
        data = yaml.safe_load(f)
    values = data["values"]

    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]

    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034

        assert (
            min_annual_growth <= growth_rate <= max_annual_growth
        ), f"CPI-U growth rate {growth_rate} outside reasonable bounds"

    # Test Chained CPI-U growth (should be lower than regular CPI-U)
    with open(
        "policyengine_us/parameters/gov/bls/cpi/c_cpi_u.yaml", encoding="utf-8"
    ) as f:
        data = yaml.safe_load(f)
    values = data["values"]

    dates_2034 = [k for k in values.keys() if k.year == 2034]
    dates_2035 = [k for k in values.keys() if k.year == 2035]

    if dates_2034 and dates_2035:
        value_2034 = values[dates_2034[0]]
        value_2035 = values[dates_2035[0]]
        growth_rate = value_2035 / value_2034

        assert (
            min_annual_growth <= growth_rate <= max_annual_growth
        ), f"Chained CPI-U growth rate {growth_rate} outside reasonable bounds"
