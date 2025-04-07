import pytest

LIMITS = [
    ("cps_2022", "2023", 3.6),
    ("cps_2022", "2024", 3.5),
    ("cps_2022", "2025", 3.4),
    ("enhanced_cps_2022", "2023", 0.005),
    ("enhanced_cps_2022", "2024", 0.001),
    ("enhanced_cps_2022", "2025", 0.001),
]


# Needs PyTorch to be installed.
@pytest.mark.skip(reason="PyTorch is not installed.")
@pytest.mark.parametrize(
    "dataset, year, limit",
    [(dataset, year, limit) for dataset, year, limit in LIMITS],
)
def test_calibration(dataset, year, limit):
    from policyengine_us_data.datasets.cps.enhanced_cps.calibrate import (
        get_snapshot,
    )

    snapshot_df = get_snapshot(dataset, year)
    total_loss = snapshot_df[snapshot_df.name == "total"]["value"].values[0]

    assert total_loss < limit
