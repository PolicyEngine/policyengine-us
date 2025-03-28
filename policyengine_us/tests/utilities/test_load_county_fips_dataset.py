from policyengine_core.tools.hugging_face import download_huggingface_dataset
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
)
from pathlib import Path
import pytest
import pandas as pd
import gzip


@pytest.fixture
def tmp_fips_dir(tmp_path) -> Path:
    """
    Create a temporary filepath for the FIPS dataset.
    Return this path as a Path object.
    """
    TMP_DIR: Path = tmp_path / "county_fips_dataset"
    TMP_DIR.mkdir()
    return TMP_DIR


@pytest.fixture
def mock_dataset_file(tmp_fips_dir) -> Path:
    """Create a small mock dataset file for testing."""

    # Create a small test CSV with the expected format
    test_data = pd.DataFrame(
        {
            "county_fips": ["01001", "02002", "03003"],
            "county_name": ["Test County 1", "Test County 2", "Test County 3"],
            "state": ["AL", "AK", "AZ"],
        }
    )

    # Save as gzipped CSV
    test_file_path = tmp_fips_dir / "county_fips_2020.csv.gz"
    with gzip.open(test_file_path, "wb") as f:
        test_data.to_csv(f, index=False, encoding="utf-8")

    return test_file_path


def mock_download_huggingface_dataset_success(filepath):
    def _mock(*args, **kwargs):
        return filepath

    return _mock


def mock_download_huggingface_dataset_failure(filepath):
    def _mock(*args, **kwargs):
        raise Exception("Download failed")

    return _mock


class TestCountyFIPSDatasetFile:
    """
    Test that the county FIPS dataset file exists and downloads properly.
    """

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


class TestLoadCountyFIPSDataset:
    """
    Test that the load_county_fips_dataset function works correctly.
    """

    def test_when_func_is_run__correctly__returns_dataframe(
        self, mock_dataset_file, monkeypatch
    ):
        """
        Test that the load_county_fips_dataset function returns a DataFrame with the correct columns.
        """

        # Apply the mock
        monkeypatch.setattr(
            "policyengine_us.tools.geography.county_helpers.download_huggingface_dataset",
            mock_download_huggingface_dataset_success(mock_dataset_file),
        )

        result = load_county_fips_dataset()

        # Verify the result is a pandas DataFrame with expected structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert (
            "01001" in result.values
        )  # Check that FIPS codes are preserved as strings

    def test_when_func_is_run__download_fails__raises_exception(
        self, mock_dataset_file, monkeypatch
    ):
        """
        Test that the load_county_fips_dataset function raises an exception when download fails.
        """

        # Apply the mock
        monkeypatch.setattr(
            "policyengine_us.tools.geography.county_helpers.download_huggingface_dataset",
            mock_download_huggingface_dataset_failure(mock_dataset_file),
        )

        with pytest.raises(Exception) as excinfo:
            load_county_fips_dataset()

        assert "Error downloading" in str(excinfo.value)
