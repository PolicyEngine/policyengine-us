import pandas as pd
import numpy as np
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from pathlib import Path
from policyengine_core.tools.hugging_face import download_huggingface_dataset


DATA_FOLDER = Path("data")
HUGGINGFACE_REPO = "policyengine/policyengine-us-data"
COUNTY_FIPS_DATASET_FILENAME = "county_fips_2020.csv.gz"
BUNDLED_COUNTY_FIPS_DATASET = Path(__file__).parent / "county_fips_2020.csv"


def load_county_fips_dataset() -> pd.DataFrame:
    """
    Load the county FIPS dataset into a pandas DataFrame.

    Prefer the bundled copy so tests and household calculations do not depend
    on a live Hugging Face request. Fall back to Hugging Face if the bundled
    file is unavailable.
    """

    if BUNDLED_COUNTY_FIPS_DATASET.exists():
        return pd.read_csv(
            BUNDLED_COUNTY_FIPS_DATASET,
            dtype={"county_fips": str},
            encoding="utf-8",
        )

    try:
        COUNTY_FIPS_RAW = download_huggingface_dataset(
            repo=HUGGINGFACE_REPO,
            repo_filename=COUNTY_FIPS_DATASET_FILENAME,
            version=None,
            local_dir=DATA_FOLDER,
        )

        # Read raw data into pandas dataframe; county FIPS MUST be defined as string,
        # else pandas reads as int and drops leading zeros
        COUNTY_FIPS_DATASET = pd.read_csv(
            COUNTY_FIPS_RAW,
            compression="gzip",
            dtype={"county_fips": str},
            encoding="utf-8",
        )

        return COUNTY_FIPS_DATASET

    except Exception as e:
        raise Exception(
            f"Error downloading {COUNTY_FIPS_DATASET_FILENAME} from {HUGGINGFACE_REPO}: {e}"
        )


def map_county_string_to_enum(
    county_name: "pd.Series[str]", state_code: "pd.Series[str]"
) -> "pd.Series[int]":
    """Helper function to map county name and state code to County enum value."""
    county_key = county_name.apply(
        lambda name: (
            name.replace(" ", "_")
            .replace("-", "_")
            .replace(".", "")
            .replace("'", "_")
            .strip()
            .upper()
        )
    )
    county_state = county_key.str.cat(state_code, sep="_")
    county_names = pd.Series(
        np.arange(len(County._member_names_)),
        index=County._member_names_,
    )
    return county_names[county_state]
