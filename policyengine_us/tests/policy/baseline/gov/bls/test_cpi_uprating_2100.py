"""Test that CPI uprating factors extend through 2100."""


def test_cpi_u_extends_to_2100():
    """Test that CPI-U extends through 2100."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test that values exist for future years
    test_years = [2035, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.bls.cpi.cpi_u(f"{year}-01-01")
        assert value > 0, f"No positive CPI-U value for year {year}"
        values.append(value)

    # Test monotonic increase over time
    for i in range(1, len(values)):
        assert (
            values[i] > values[i - 1]
        ), f"CPI-U should increase from {test_years[i-1]} to {test_years[i]}"


def test_chained_cpi_u_extends_to_2100():
    """Test that Chained CPI-U extends through 2100."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test that values exist for future years
    test_years = [2035, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.bls.cpi.c_cpi_u(f"{year}-01-01")
        assert value > 0, f"No positive Chained CPI-U value for year {year}"
        values.append(value)

    # Test monotonic increase
    for i in range(1, len(values)):
        assert (
            values[i] > values[i - 1]
        ), f"Chained CPI-U should increase from {test_years[i-1]} to {test_years[i]}"


def test_cpi_w_extends_to_2100():
    """Test that CPI-W extends through 2100."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test that values exist for future years
    test_years = [2035, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.bls.cpi.cpi_w(f"{year}-01-01")
        assert value > 0, f"No positive CPI-W value for year {year}"
        values.append(value)

    # Test monotonic increase
    for i in range(1, len(values)):
        assert (
            values[i] > values[i - 1]
        ), f"CPI-W should increase from {test_years[i-1]} to {test_years[i]}"


def test_uprating_growth_rates_are_reasonable():
    """Test that all uprating growth rates are within reasonable bounds."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Annual growth rates should be between 0.5% and 5% for inflation measures
    # Using wider bounds to be less brittle
    min_annual_growth = 1.005
    max_annual_growth = 1.05

    # Test CPI-U growth in extended period
    year1, year2 = 2050, 2051
    value_year1 = parameters.gov.bls.cpi.cpi_u(f"{year1}-01-01")
    value_year2 = parameters.gov.bls.cpi.cpi_u(f"{year2}-01-01")
    growth_rate = value_year2 / value_year1

    assert (
        min_annual_growth <= growth_rate <= max_annual_growth
    ), f"CPI-U growth rate {growth_rate} outside reasonable bounds"

    # Test Chained CPI-U growth
    value_year1 = parameters.gov.bls.cpi.c_cpi_u(f"{year1}-01-01")
    value_year2 = parameters.gov.bls.cpi.c_cpi_u(f"{year2}-01-01")
    growth_rate = value_year2 / value_year1

    assert (
        min_annual_growth <= growth_rate <= max_annual_growth
    ), f"Chained CPI-U growth rate {growth_rate} outside reasonable bounds"
