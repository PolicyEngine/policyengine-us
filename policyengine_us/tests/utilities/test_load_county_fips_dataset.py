import gzip
from pathlib import Path

import pandas as pd
import pytest

from policyengine_us.tools.geography import county_helpers
from policyengine_us.tools.geography.county_helpers import (
    COUNTY_FIPS_DATASET_FILENAME,
    load_county_fips_dataset,
)


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
    test_file_path = tmp_fips_dir / COUNTY_FIPS_DATASET_FILENAME
    with gzip.open(test_file_path, "wb") as f:
        test_data.to_csv(f, index=False, encoding="utf-8")

    return test_file_path


class TestLoadCountyFIPSDataset:
    """
    Test that the load_county_fips_dataset function works correctly.
    """

    def test_when_local_data_file_exists__returns_local_dataframe(
        self, mock_dataset_file, monkeypatch
    ):
        """
        Test that the load_county_fips_dataset function reads a local data file when present.
        """

        monkeypatch.setattr(
            county_helpers,
            "DATA_FOLDER",
            mock_dataset_file.parent,
        )

        result = load_county_fips_dataset()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert (
            "01001" in result.values
        )  # Check that FIPS codes are preserved as strings

    def test_when_local_data_file_is_missing__returns_packaged_dataframe(
        self, tmp_fips_dir, monkeypatch
    ):
        """
        Test that the packaged dataset is used when no local data file exists.
        """

        monkeypatch.setattr(
            county_helpers,
            "DATA_FOLDER",
            tmp_fips_dir,
        )

        result = load_county_fips_dataset()

        assert isinstance(result, pd.DataFrame)
        assert {"county_fips", "county_name", "state"}.issubset(result.columns)
        assert len(result) > 3_000
        assert "01001" in result["county_fips"].values
        assert "06037" in result["county_fips"].values
        assert all(isinstance(fips, str) for fips in result["county_fips"])
