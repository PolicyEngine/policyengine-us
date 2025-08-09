"""Test that CPI uprating factors extend through 2100."""

import yaml


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

    # Test consistent growth in extended period
    years = [2045, 2046, 2047]
    consecutive_vals = []
    for year in years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            consecutive_vals.append(values[dates[0]])

    if len(consecutive_vals) == 3:
        growth1 = consecutive_vals[1] / consecutive_vals[0]
        growth2 = consecutive_vals[2] / consecutive_vals[1]
        assert abs(growth1 - growth2) < 0.001, "Growth should be consistent"


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
