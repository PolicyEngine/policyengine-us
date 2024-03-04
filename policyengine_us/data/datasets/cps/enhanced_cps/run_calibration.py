from policyengine_us.data.datasets.cps.enhanced_cps.loss import (
    get_snapshot,
)
from policyengine_us.data.storage import STORAGE_FOLDER
import pandas as pd


def main():
    for file in STORAGE_FOLDER.glob("*.h5"):
        file.unlink()

    for file in STORAGE_FOLDER.glob("*.csv.gz"):
        file.unlink()

    YEARS = ["2022", "2023", "2024", "2025"]
    DATASETS = ["puf_2023", "cps_2023", "calibrated_puf_extended_cps_2022"]

    dfs = []

    for year in YEARS:
        for dataset in DATASETS:
            df = get_snapshot(dataset, year)
            df["time_period"] = year
            df["dataset"] = dataset
            dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    df.to_csv(
        STORAGE_FOLDER / "dataset_losses.csv.gz",
        index=False,
        compression="gzip",
    )


if __name__ == "__main__":
    main()
