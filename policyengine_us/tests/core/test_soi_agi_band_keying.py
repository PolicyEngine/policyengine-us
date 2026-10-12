"""The IRS SOI AGI-band calibration scales hold their published values in the
tax year they come from.

``calibration.gov.irs.soi.agi.total_agi`` holds tax year 2020 values from IRS
SOI Publication 1304 Table 1.1 and ``number_of_returns`` holds tax year 2021
values. ``uprate_parameters`` grows each amount forward from its latest dated
value, so keying a scale to a year before its data inflates every later year:
``total_agi`` sat at 2015-01-01 and its 2020 amounts were about 40% above the
published table. ``CountryTaxBenefitSystem`` then backdates each parameter's
earliest value to 2015-01-01, so years before the first dated amount still
evaluate.
"""

from datetime import date
from pathlib import Path

import pytest
import yaml

from policyengine_us.system import system as SYSTEM

SOI_AGI_DIR = (
    Path(__file__).resolve().parents[2] / "parameters/calibration/gov/irs/soi/agi"
)
CASES = {
    "total_agi": (2020, "calibration.gov.cbo.income_by_source.adjusted_gross_income"),
    "number_of_returns": (2021, "calibration.gov.census.populations.total"),
}


def _amount_values(name):
    parameter = yaml.safe_load((SOI_AGI_DIR / f"{name}.yaml").read_text())
    return [bracket["amount"]["values"] for bracket in parameter["brackets"]]


def _scale(name):
    return getattr(SYSTEM.parameters.calibration.gov.irs.soi.agi, name)


def _uprating_index(path):
    node = SYSTEM.parameters
    for key in path.split("."):
        node = getattr(node, key)
    return node


@pytest.mark.parametrize("name", CASES)
def test_soi_agi_band_holds_published_values_in_its_tax_year(name):
    tax_year, _ = CASES[name]
    key = date(tax_year, 1, 1)
    amounts = _amount_values(name)

    assert all(key in values for values in amounts), f"{name} lacks {key} amounts"
    assert _scale(name)(f"{tax_year}-01-01").amounts == [
        values[key] for values in amounts
    ]


@pytest.mark.parametrize("name", CASES)
def test_soi_agi_band_uprates_from_its_latest_value(name):
    _, index_path = CASES[name]
    latest = max(max(values) for values in _amount_values(name)).year
    scale = _scale(name)
    index = _uprating_index(index_path)
    anchor = f"{latest}-01-01"
    later = f"{latest + 5}-01-01"
    growth = index(later) / index(anchor)

    assert scale(later).amounts == pytest.approx(
        [amount * growth for amount in scale(anchor).amounts]
    )


@pytest.mark.parametrize("name", CASES)
def test_soi_agi_band_evaluates_before_its_first_value(name):
    earliest = min(min(values) for values in _amount_values(name)).year
    scale = _scale(name)
    at_earliest = scale(f"{earliest}-01-01")

    for year in range(2015, earliest):
        earlier = scale(f"{year}-01-01")
        assert earlier.thresholds == at_earliest.thresholds, year
        assert earlier.amounts == at_earliest.amounts, year
