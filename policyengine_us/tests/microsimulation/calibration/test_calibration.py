import pytest

DATASETS = ["cps_2023"]
YEARS = ["2023", "2024", "2025"]


@pytest.mark.parametrize(
    "dataset, year",
    [(dataset, year) for dataset in DATASETS for year in YEARS],
)
def test_calibration(dataset, year):
    from policyengine_us.data.datasets.cps.enhanced_cps.calibrate import (
        get_snapshot,
    )

    snapshot_df = get_snapshot(dataset, "2023")
    total_loss = snapshot_df[snapshot_df.name == "total"]["value"].values[0]

    assert total_loss < 0
