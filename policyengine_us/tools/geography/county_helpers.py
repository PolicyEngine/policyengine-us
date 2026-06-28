from importlib import resources
from pathlib import Path

import pandas as pd


DATA_FOLDER = Path("data")
COUNTY_FIPS_DATASET_FILENAME = "county_fips_2020.csv.gz"
COUNTY_FIPS_PACKAGE = "policyengine_us.data"


def _read_county_fips_dataset(dataset_file) -> pd.DataFrame:
    return pd.read_csv(
        dataset_file,
        compression="gzip",
        dtype={"county_fips": str},
        encoding="utf-8",
    )


def load_county_fips_dataset() -> pd.DataFrame:
    """
    Load the county FIPS dataset into a pandas DataFrame.
    If the dataset exists in the 'data' folder, load that local copy. Otherwise,
    use the packaged fallback so runtime county lookup does not require network access.
    """

    local_dataset = DATA_FOLDER / COUNTY_FIPS_DATASET_FILENAME
    if local_dataset.is_file():
        return _read_county_fips_dataset(local_dataset)

    package_dataset = resources.files(COUNTY_FIPS_PACKAGE).joinpath(
        COUNTY_FIPS_DATASET_FILENAME
    )
    with package_dataset.open("rb") as dataset_file:
        return _read_county_fips_dataset(dataset_file)
