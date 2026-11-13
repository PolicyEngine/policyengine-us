"""Test the Excel-to-CSV adapter without loading Excel or constructing simulations."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


MODULE_PATH = Path(__file__).parents[2] / "tools" / "convert_hud_fmr_xlsx.py"
SPEC = importlib.util.spec_from_file_location("hud_fmr_converter", MODULE_PATH)
converter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(converter)


@pytest.mark.parametrize(
    "state_column,area_column,rent_prefix",
    [("state_alpha", "fips2010", "fmr"), ("stusps", "fips", "fmr_")],
)
def test_historical_and_current_columns_preserve_all_bedrooms(
    state_column, area_column, rent_prefix
):
    # Synthetic values isolate column mapping, not a policy calculation.
    raw = pd.DataFrame(
        {
            state_column: ["CA", "AS"],
            area_column: ["0603799999", "60010"],
            **{
                f"{rent_prefix}{bedroom}": [100 + bedroom, 200 + bedroom]
                for bedroom in range(5)
            },
        }
    )
    result = converter.reshape(raw, 2017)
    assert len(result) == 10
    for state, area, base in [("CA", "603799999", 100), ("AS", "60010", 200)]:
        rows = result[result.state == state]
        assert rows.hud_fmr_area_code.tolist() == [area] * 5
        assert rows.bedrooms.tolist() == list(range(5))
        assert rows.value.tolist() == [base + bedroom for bedroom in range(5)]
        assert rows.year.tolist() == [2017] * 5


def test_merge_keeps_other_vintages_and_replaces_only_identical_key(tmp_path):
    output = tmp_path / "rents.csv"
    pd.DataFrame(
        [("CA", "603799999", 2025, 2, 900), ("AS", "60010", 2017, 2, 800)],
        columns=["state", "hud_fmr_area_code", "year", "bedrooms", "value"],
    ).to_csv(output, index=False)
    new = pd.DataFrame(
        [("AS", "60010", 2017, 2, 700), ("CA", "603799999", 2017, 2, 600)],
        columns=["state", "hud_fmr_area_code", "year", "bedrooms", "value"],
    )
    merged = converter.merge_with_existing(new, output)
    assert list(merged.itertuples(index=False, name=None)) == [
        ("AS", "60010", 2017, 2, 700),
        ("CA", "603799999", 2017, 2, 600),
        ("CA", "603799999", 2025, 2, 900),
    ]


def test_read_sheet_skips_metadata_and_normalizes_historical_headers(monkeypatch):
    class Workbook:
        sheet_names = ["Field_Descriptions", "EXCEL_DATA"]

        def parse(self, sheet):
            if sheet == "Field_Descriptions":
                return pd.DataFrame({"Description": ["metadata"]})
            return pd.DataFrame(
                {"STATE_ALPHA": ["CA"], "FIPS2010": ["0603799999"], "FMR0": [100]}
            )

    def excel_file(path, engine):
        assert engine == "calamine"
        return Workbook()

    monkeypatch.setattr(converter.pd, "ExcelFile", excel_file)
    assert converter.read_sheet(Path("synthetic.xlsx")).columns.tolist() == [
        "state_alpha",
        "fips2010",
        "fmr0",
    ]
