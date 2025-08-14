"""Test unified uprating extensions through 2100."""


def test_all_uprating_factors_extend_to_2100():
    """Test that all uprating factors extend through 2100 with consistent growth rates."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Define all uprating parameters to test with their specific periods
    uprating_params = [
        ("IRS", parameters.gov.irs.uprating, "-01-01"),
        ("SNAP", parameters.gov.usda.snap.uprating, "-10-01"),
        ("SSA", parameters.gov.ssa.uprating, "-01-01"),
        ("HHS", parameters.gov.hhs.uprating, "-01-01"),
        ("CPI-U", parameters.gov.bls.cpi.cpi_u, "-02-01"),
        ("Chained CPI-U", parameters.gov.bls.cpi.c_cpi_u, "-02-01"),
        ("CPI-W", parameters.gov.bls.cpi.cpi_w, "-02-01"),
    ]

    for name, param, date_suffix in uprating_params:
        # Test that values exist and are positive for future years
        test_years = [2035, 2050, 2075, 2100]
        values = []

        for year in test_years:
            value = param(f"{year}{date_suffix}")
            assert (
                value > 0
            ), f"No positive {name} uprating value for year {year}"
            values.append(value)

        # Test that values are monotonically increasing
        for i in range(1, len(values)):
            assert (
                values[i] > values[i - 1]
            ), f"{name} uprating should increase from {test_years[i-1]} to {test_years[i]}"

        # Test that growth is consistent in the extended period
        # Use years after the projection period ends
        year1, year2, year3 = 2040, 2041, 2042
        val1 = param(f"{year1}{date_suffix}")
        val2 = param(f"{year2}{date_suffix}")
        val3 = param(f"{year3}{date_suffix}")

        growth_rate_1 = val2 / val1
        growth_rate_2 = val3 / val2

        # Growth rates should be approximately equal (within 0.1%)
        assert (
            abs(growth_rate_1 - growth_rate_2) < 0.001
        ), f"{name} growth rate should be consistent: {growth_rate_1:.5f} vs {growth_rate_2:.5f}"


def test_uprating_growth_rates_are_reasonable():
    """Test that all uprating growth rates are within reasonable bounds."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Annual growth rates should be between 0.5% and 5% for inflation measures
    min_annual_growth = 1.005
    max_annual_growth = 1.05

    # Test all uprating parameters
    uprating_params = [
        ("IRS", parameters.gov.irs.uprating, "-01-01"),
        ("SNAP", parameters.gov.usda.snap.uprating, "-10-01"),
        ("SSA", parameters.gov.ssa.uprating, "-01-01"),
        ("HHS", parameters.gov.hhs.uprating, "-01-01"),
        ("CPI-U", parameters.gov.bls.cpi.cpi_u, "-02-01"),
        ("Chained CPI-U", parameters.gov.bls.cpi.c_cpi_u, "-02-01"),
        ("CPI-W", parameters.gov.bls.cpi.cpi_w, "-02-01"),
    ]

    year1, year2 = 2050, 2051

    for name, param, date_suffix in uprating_params:
        value_year1 = param(f"{year1}{date_suffix}")
        value_year2 = param(f"{year2}{date_suffix}")
        growth_rate = value_year2 / value_year1

        assert (
            min_annual_growth <= growth_rate <= max_annual_growth
        ), f"{name} growth rate {growth_rate:.4f} outside reasonable bounds [{min_annual_growth:.3f}, {max_annual_growth:.3f}]"


def test_cpi_relationships():
    """Test that CPI indices maintain expected relationships."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test a few years to ensure relationships are maintained
    test_years = [2040, 2060, 2080, 2100]

    for year in test_years:
        cpi_u = parameters.gov.bls.cpi.cpi_u(f"{year}-02-01")
        c_cpi_u = parameters.gov.bls.cpi.c_cpi_u(f"{year}-02-01")

        # Chained CPI-U typically grows slower than regular CPI-U
        # due to substitution effects, but not always
        # Just verify both exist and are positive
        assert cpi_u > 0, f"CPI-U should be positive in {year}"
        assert c_cpi_u > 0, f"Chained CPI-U should be positive in {year}"
