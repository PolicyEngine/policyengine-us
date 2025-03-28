from policyengine_core.tools.hugging_face import download_huggingface_dataset
from pathlib import Path
import pytest
import pandas as pd


@pytest.fixture
def tmp_fips_dir(tmp_path) -> Path:
    """
    Create a temporary filepath for the FIPS dataset.
    Return this path as a Path object.
    """
    TMP_DIR: Path = tmp_path / "county_fips_dataset"
    TMP_DIR.mkdir()
    return TMP_DIR


# Ensure dataset exists and is accessible
class TestCountyFIPSDataset:

    HUGGINGFACE_REPO = "policyengine/policyengine-us-data"
    COUNTY_FIPS_DATASET_FILENAME = "county_fips_2020.csv.gz"

    def test_when_downloading_county_fips__download_is_successful(
        self, tmp_fips_dir
    ):

        download_huggingface_dataset(
            repo=self.HUGGINGFACE_REPO,
            repo_filename=self.COUNTY_FIPS_DATASET_FILENAME,
            version=None,
            local_dir=tmp_fips_dir,
        )

        TMP_FILE = tmp_fips_dir / self.COUNTY_FIPS_DATASET_FILENAME
        assert TMP_FILE.is_file()

    def test_when_downloading_and_parsing_county_fips__result_is_correct(
        self, tmp_fips_dir
    ):

        download_huggingface_dataset(
            repo=self.HUGGINGFACE_REPO,
            repo_filename=self.COUNTY_FIPS_DATASET_FILENAME,
            version=None,
            local_dir=tmp_fips_dir,
        )

        TMP_FILE = tmp_fips_dir / self.COUNTY_FIPS_DATASET_FILENAME

        df = pd.read_csv(
            TMP_FILE,
            compression="gzip",
            dtype={"county_fips": str},
            encoding="utf-8",
            nrows=5,  # Just read a few rows
        )

        assert "county_fips" in df.columns
        assert len(df) > 0

        # Check FIPS codes are properly preserved as strings
        assert all(isinstance(fips, str) for fips in df["county_fips"])


# When downloading a correctly formatted file, the function should return a pandas DataFrame with the correct columns.

# When download error occurs, function should throw error
