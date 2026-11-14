"""Test the standalone archive adapter without requiring an optional Excel engine."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

# Import the standalone adapter directly: importing policyengine_us would build
# system.py's module-level CountryTaxBenefitSystem during test collection.
MODULE = (
    Path(__file__).resolve().parents[2] / "tools" / "convert_hud_income_limits_xlsx.py"
)
SPEC = importlib.util.spec_from_file_location("hud_income_limits_converter", MODULE)
converter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(converter)


def source_rows(geography_column):
    """Synthetic rows isolate column names, leading zeros, and county aggregation."""
    columns = {
        geography_column: ["0100199999", "0900100001", "0900100002"],
        "median2017": [60_000, 90_000, 100_000],
    }
    for prefix, base in [("ELI", 1_000), ("l50", 5_000), ("l80", 9_000)]:
        for size in range(1, 9):
            amount = base + size * 10
            columns[f"{prefix}_{size}"] = [amount, amount + 1_000, amount + 1_100]
    return pd.DataFrame(columns)


@pytest.mark.parametrize("geography_column", ["fips", "fips2010"])
def test_selects_section8_sheet_with_current_or_archive_header(
    geography_column, monkeypatch, tmp_path
):
    original = source_rows(geography_column)
    sheets = {"Notes": pd.DataFrame({"note": ["not the data"]}), "Limits": original}
    workbook = SimpleNamespace(sheet_names=list(sheets), parse=sheets.__getitem__)
    monkeypatch.setattr(converter.pd, "ExcelFile", lambda *args, **kwargs: workbook)

    pd.testing.assert_frame_equal(converter.read_sheet(tmp_path / "hud.xlsx"), original)


@pytest.mark.parametrize("geography_column", ["fips", "fips2010"])
def test_archive_mapping_preserves_fips_and_collapses_subcounty_rows(geography_column):
    original = source_rows(geography_column)
    converted = converter.reshape(original, 2017)

    assert converted["county_fips"].tolist() == ["01001", "09001"]
    assert converted["year"].tolist() == [2017, 2017]
    assert converted["ami"].tolist() == [60_000, 95_000]
    assert converted["extremely_low_income_1"].tolist() == [1_010, 2_060]
    assert converted["very_low_income_8"].tolist() == [5_080, 6_130]
    assert converted["low_income_4"].tolist() == [9_040, 10_090]
    assert geography_column in original.columns


def test_archive_missing_published_size_column_is_rejected():
    incomplete = source_rows("fips2010").drop(columns="ELI_8")

    with pytest.raises(KeyError, match="ELI_8"):
        converter.reshape(incomplete, 2017)
