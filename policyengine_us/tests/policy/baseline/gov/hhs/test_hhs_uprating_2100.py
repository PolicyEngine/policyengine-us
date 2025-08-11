"""Test that HHS uprating factors extend through 2100."""


def test_hhs_uprating_extends_to_2100():
    """Test that HHS uprating factors extend through 2100."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test that values exist and are positive for future years
    test_years = [2035, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.hhs.uprating(f"{year}-01-01")
        assert value > 0, f"No positive HHS uprating value for year {year}"
        values.append(value)

    # Test that values are monotonically increasing
    for i in range(1, len(values)):
        assert (
            values[i] > values[i - 1]
        ), f"HHS uprating should increase over time"

    # Test that growth is consistent in the extended period
    year1, year2, year3 = 2040, 2041, 2042
    val1 = parameters.gov.hhs.uprating(f"{year1}-01-01")
    val2 = parameters.gov.hhs.uprating(f"{year2}-01-01")
    val3 = parameters.gov.hhs.uprating(f"{year3}-01-01")

    growth_rate_1 = val2 / val1
    growth_rate_2 = val3 / val2

    # Growth rates should be approximately equal (within 0.1%)
    assert (
        abs(growth_rate_1 - growth_rate_2) < 0.001
    ), "Growth rate should be consistent"
