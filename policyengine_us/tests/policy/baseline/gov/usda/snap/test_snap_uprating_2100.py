"""Test that SNAP uprating factors extend through 2100."""

import yaml
from datetime import date


def test_snap_uprating_extends_to_2100():
    """Test that SNAP uprating factors extend through 2100."""
    # Load the SNAP uprating YAML file
    with open(
        "policyengine_us/parameters/gov/usda/snap/uprating.yaml",
        encoding="utf-8",
    ) as f:
        data = yaml.safe_load(f)

    values = data["values"]

    # Check that we have values for key years
    dates_2100 = [k for k in values.keys() if k.year == 2100]
    assert len(dates_2100) > 0, "No 2100 values found in SNAP uprating"

    # Get the 2100 value
    date_2100 = dates_2100[0]
    value_2100 = values[date_2100]

    # Should be significantly higher than 2034 value (391.3)
    assert (
        value_2100 > 1600
    ), f"2100 SNAP uprating value {value_2100} seems too low"

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
            expected_2050 = value_2034 * (expected_growth**16)
            assert abs(value_2050 - expected_2050) / expected_2050 < 0.01
