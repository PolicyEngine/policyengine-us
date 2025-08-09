"""Tests for uprating factor extensions through 2100."""

import yaml
from policyengine_us.model_api import *
from policyengine_us.parameters.gov.irs.uprating import (
    set_irs_uprating_parameter,
)


def test_irs_uprating_extends_to_2100():
    """Test that IRS uprating factors extend through 2100."""
    # Create a microsimulation and get parameters
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Apply the uprating parameter updates
    parameters = set_irs_uprating_parameter(parameters)

    # Test that values exist and are positive for future years
    test_years = [2035, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.irs.uprating(f"{year}-01-01")
        assert value > 0, f"No positive uprating value for year {year}"
        values.append(value)

    # Test that values are monotonically increasing
    for i in range(1, len(values)):
        assert values[i] > values[i - 1], f"Uprating should increase over time"

    # Test that growth is consistent in the extended period
    # Pick any three consecutive years after the projection period
    year1, year2, year3 = 2040, 2041, 2042
    val1 = parameters.gov.irs.uprating(f"{year1}-01-01")
    val2 = parameters.gov.irs.uprating(f"{year2}-01-01")
    val3 = parameters.gov.irs.uprating(f"{year3}-01-01")

    growth_rate_1 = val2 / val1
    growth_rate_2 = val3 / val2

    # Growth rates should be approximately equal (within 0.1%)
    assert (
        abs(growth_rate_1 - growth_rate_2) < 0.001
    ), "Growth rate should be consistent"


def test_snap_uprating_extends_to_2100():
    """Test that SNAP uprating factors extend through 2100."""
    # Load the SNAP uprating YAML file
    with open(
        "policyengine_us/parameters/gov/usda/snap/uprating.yaml",
        encoding="utf-8",
    ) as f:
        data = yaml.safe_load(f)

    values = data["values"]

    # Check that we have values for year 2100
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in SNAP uprating"

    # Get values for several years to test monotonic increase
    test_years = [2030, 2050, 2075, 2100]
    year_values = []

    for year in test_years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            year_values.append((year, values[dates[0]]))

    # Test that values are monotonically increasing
    for i in range(1, len(year_values)):
        assert (
            year_values[i][1] > year_values[i - 1][1]
        ), f"SNAP uprating should increase from {year_values[i-1][0]} to {year_values[i][0]}"

    # Test that growth rate is consistent in extended period
    # Get three consecutive years after 2040
    years_to_test = [2045, 2046, 2047]
    consecutive_values = []

    for year in years_to_test:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            consecutive_values.append(values[dates[0]])

    if len(consecutive_values) == 3:
        growth1 = consecutive_values[1] / consecutive_values[0]
        growth2 = consecutive_values[2] / consecutive_values[1]
        assert (
            abs(growth1 - growth2) < 0.001
        ), "Growth rate should be consistent"


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

    # Test monotonic increase over time
    test_years = [2035, 2050, 2075, 2100]
    year_values = []

    for year in test_years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            year_values.append((year, values[dates[0]]))

    for i in range(1, len(year_values)):
        assert (
            year_values[i][1] > year_values[i - 1][1]
        ), f"CPI-U should increase from {year_values[i-1][0]} to {year_values[i][0]}"


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

    # Test monotonic increase
    test_years = [2035, 2050, 2075, 2100]
    year_values = []

    for year in test_years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            year_values.append((year, values[dates[0]]))

    for i in range(1, len(year_values)):
        assert (
            year_values[i][1] > year_values[i - 1][1]
        ), f"Chained CPI-U should increase from {year_values[i-1][0]} to {year_values[i][0]}"


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

    # Test monotonic increase
    test_years = [2035, 2050, 2075, 2100]
    year_values = []

    for year in test_years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            year_values.append((year, values[dates[0]]))

    # Only test if we have enough values
    if len(year_values) > 1:
        for i in range(1, len(year_values)):
            assert (
                year_values[i][1] > year_values[i - 1][1]
            ), f"CPI-W should increase from {year_values[i-1][0]} to {year_values[i][0]}"


def test_uprating_growth_rates_are_reasonable():
    """Test that all uprating growth rates are within reasonable bounds."""
    # Annual growth rates should be between 0.5% and 5% for inflation measures
    # Using wider bounds to be less brittle
    min_annual_growth = 1.005
    max_annual_growth = 1.05

    # Test CPI-U growth in extended period
    with open(
        "policyengine_us/parameters/gov/bls/cpi/cpi_u.yaml", encoding="utf-8"
    ) as f:
        data = yaml.safe_load(f)
    values = data["values"]

    # Check growth between any two consecutive years after 2040
    year1, year2 = 2050, 2051
    dates_year1 = [k for k in values.keys() if k.year == year1]
    dates_year2 = [k for k in values.keys() if k.year == year2]

    if dates_year1 and dates_year2:
        value_year1 = values[dates_year1[0]]
        value_year2 = values[dates_year2[0]]
        growth_rate = value_year2 / value_year1

        assert (
            min_annual_growth <= growth_rate <= max_annual_growth
        ), f"CPI-U growth rate {growth_rate} outside reasonable bounds"

    # Test Chained CPI-U growth
    with open(
        "policyengine_us/parameters/gov/bls/cpi/c_cpi_u.yaml", encoding="utf-8"
    ) as f:
        data = yaml.safe_load(f)
    values = data["values"]

    dates_year1 = [k for k in values.keys() if k.year == year1]
    dates_year2 = [k for k in values.keys() if k.year == year2]

    if dates_year1 and dates_year2:
        value_year1 = values[dates_year1[0]]
        value_year2 = values[dates_year2[0]]
        growth_rate = value_year2 / value_year1

        assert (
            min_annual_growth <= growth_rate <= max_annual_growth
        ), f"Chained CPI-U growth rate {growth_rate} outside reasonable bounds"
