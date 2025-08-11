"""Test that SNAP uprating factors extend through 2100."""


def test_snap_uprating_extends_to_2100():
    """Test that SNAP uprating factors extend through 2100."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    parameters = sim.tax_benefit_system.parameters

    # Test that values exist and are positive for future years
    test_years = [2030, 2050, 2075, 2100]
    values = []

    for year in test_years:
        value = parameters.gov.usda.snap.uprating(f"{year}-10-01")
        assert value > 0, f"No positive SNAP uprating value for year {year}"
        values.append(value)

    # Test that values are monotonically increasing
    for i in range(1, len(values)):
        assert (
            values[i] > values[i - 1]
        ), f"SNAP uprating should increase from year {test_years[i-1]} to {test_years[i]}"

    # Test that growth rate is consistent in extended period
    # Get three consecutive years after 2040
    years_to_test = [2045, 2046, 2047]
    consecutive_values = []

    for year in years_to_test:
        consecutive_values.append(
            parameters.gov.usda.snap.uprating(f"{year}-10-01")
        )

    growth1 = consecutive_values[1] / consecutive_values[0]
    growth2 = consecutive_values[2] / consecutive_values[1]
    # Growth rates should be approximately equal (within 0.1%)
    assert (
        abs(growth1 - growth2) < 0.001
    ), f"Growth rate should be consistent: {growth1:.5f} vs {growth2:.5f}"
