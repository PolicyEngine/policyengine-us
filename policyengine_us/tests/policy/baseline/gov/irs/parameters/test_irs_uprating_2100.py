"""Test that IRS uprating factors extend through 2100."""

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
