"""Test that SNAP uprating factors extend through 2100."""

import yaml


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

    # Test monotonic increase over time
    test_years = [2030, 2050, 2075, 2100]
    year_values = []

    for year in test_years:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            year_values.append((year, values[dates[0]]))

    # Verify values increase over time
    for i in range(1, len(year_values)):
        assert (
            year_values[i][1] > year_values[i - 1][1]
        ), f"SNAP uprating should increase from {year_values[i-1][0]} to {year_values[i][0]}"

    # Test that growth rate is consistent in extended period
    # Pick any three consecutive years after 2040
    years_to_test = [2045, 2046, 2047]
    consecutive_values = []

    for year in years_to_test:
        dates = [k for k in values.keys() if k.year == year]
        if dates:
            consecutive_values.append(values[dates[0]])

    if len(consecutive_values) == 3:
        growth1 = consecutive_values[1] / consecutive_values[0]
        growth2 = consecutive_values[2] / consecutive_values[1]
        # Growth rates should be approximately equal (within 0.1%)
        assert (
            abs(growth1 - growth2) < 0.001
        ), f"Growth rate should be consistent: {growth1:.5f} vs {growth2:.5f}"
