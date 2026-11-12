"""Check Core's uprating of filing-status parameter children.

Household YAML tests cannot read parameter values directly. These tests reuse
the built system to check projections, rounding and preservation of authored
values without constructing another model or household simulation.
"""

from pathlib import Path

import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import get_parameter

from policyengine_us.system import system


STATUSES = (
    "SINGLE",
    "SEPARATE",
    "JOINT",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)
CO_PATH = "gov.states.co.tax.income.subtractions.collegeinvest_contribution.max_amount"
PEP_PATH = "gov.irs.income.exemption.phase_out.start"
BIDEN_PATH = "gov.contrib.biden.budget_2025.capital_gains.income_threshold"
PEP_ANCHORS = {
    "SINGLE": 406_200,
    "SEPARATE": 243_700,
    "JOINT": 487_400,
    "HEAD_OF_HOUSEHOLD": 446_800,
    "SURVIVING_SPOUSE": 487_400,
}
PARAMETER_ROOT = Path(__file__).resolve().parents[2] / "parameters"
PROPERTY_SETTINGS = {
    "max_examples": 20,
    "deadline": None,
    "derandomize": True,
    "database": None,
}


def _value(path, status, year):
    return get_parameter(system.parameters, f"{path}.{status}")(f"{year}-01-01")


def _irs_factor(year, anchor_year):
    index = system.parameters.gov.irs.uprating
    return index(f"{year}-01-01") / index(f"{anchor_year}-01-01")


def _authored_values():
    cases = []
    for path in (CO_PATH, PEP_PATH, BIDEN_PATH):
        filename = PARAMETER_ROOT / f"{path.replace('.', '/')}.yaml"
        data = yaml.safe_load(filename.read_text())
        for status in STATUSES:
            for date, entry in data[status]["values"].items():
                value = entry["value"] if isinstance(entry, dict) else entry
                cases.append((path, status, str(date), value))
    return tuple(cases)


AUTHORED_VALUES = _authored_values()


@pytest.mark.parametrize("status", STATUSES)
def test_colorado_2027_projects_from_published_2026_limit(status):
    # Colorado publishes $39,200 for joint filers and $26,200 otherwise.
    # The retained IRS-index proxy rounds the projected amount to $100.
    # 26,200 * 181.97958333333335 / 176.71308333333332 = 26,980.8267 -> 27,000.
    # 39,200 * 181.97958333333335 / 176.71308333333332 = 40,368.2598 -> 40,400.
    anchor = 39_200 if status == "JOINT" else 26_200
    expected = 40_400 if status == "JOINT" else 27_000
    assert _value(CO_PATH, status, 2027) == expected
    assert expected > anchor


@pytest.mark.parametrize("status", STATUSES)
def test_personal_exemption_2036_projects_after_last_cbo_forecast(status):
    # CBO's last forecast supplies the 2035 anchors. Historical IRC 68(b)
    # rounds down to $50; separate filers receive half the joint amount.
    # Multiply by 217.05 / 212.85, then round down:
    # single: 406,200 * factor = 414,215.222 -> 414,200;
    # separate: 243,700 * factor = 248,508.739 -> 248,500;
    # joint/surviving spouse: 487,400 * factor = 497,017.477 -> 497,000;
    # head of household: 446,800 * factor = 455,616.350 -> 455,600.
    expected = {
        "SINGLE": 414_200,
        "SEPARATE": 248_500,
        "JOINT": 497_000,
        "HEAD_OF_HOUSEHOLD": 455_600,
        "SURVIVING_SPOUSE": 497_000,
    }[status]
    assert _value(PEP_PATH, status, 2036) == expected
    assert expected > PEP_ANCHORS[status]


@pytest.mark.parametrize("status", STATUSES)
def test_biden_2025_projects_from_proposed_2024_threshold(status):
    # Treasury's FY2025 proposal indexes $1 million ($500,000 for separate
    # filers) after 2024 and specifies no rounding interval.
    # 1,000,000 * 172.797 / 167.95475 = 1,028,830.6820735942;
    # separate filers receive half: 514,415.3410367971.
    anchor = 500_000 if status == "SEPARATE" else 1_000_000
    expected = 514_415.3410367971 if status == "SEPARATE" else 1_028_830.6820735942
    assert _value(BIDEN_PATH, status, 2025) == pytest.approx(
        expected, rel=1e-12, abs=1e-8
    )
    assert expected > anchor


@settings(**PROPERTY_SETTINGS)
@given(year=st.integers(2027, 2050), status=st.sampled_from(STATUSES))
def test_colorado_projection_rounding_bounds_and_order(year, status):
    anchor = 39_200 if status == "JOINT" else 26_200
    value = _value(CO_PATH, status, year)
    unrounded = anchor * _irs_factor(year, 2026)
    assert value % 100 == 0
    assert abs(value - unrounded) <= 50
    assert value >= _value(CO_PATH, status, year - 1)
    assert value > anchor
    assert _value(CO_PATH, "SURVIVING_SPOUSE", year) == _value(CO_PATH, "SINGLE", year)


@settings(**PROPERTY_SETTINGS)
@given(year=st.integers(2036, 2050), status=st.sampled_from(STATUSES))
def test_personal_exemption_projection_rounding_bounds_and_order(year, status):
    value = _value(PEP_PATH, status, year)
    interval = 25 if status == "SEPARATE" else 50
    unrounded = PEP_ANCHORS[status] * _irs_factor(year, 2035)
    assert value % interval == 0
    assert 0 <= unrounded - value < interval
    assert value >= _value(PEP_PATH, status, year - 1)
    assert value > PEP_ANCHORS[status]
    joint = _value(PEP_PATH, "JOINT", year)
    assert _value(PEP_PATH, "SEPARATE", year) == joint / 2
    assert _value(PEP_PATH, "SURVIVING_SPOUSE", year) == joint


@settings(**PROPERTY_SETTINGS)
@given(year=st.integers(2025, 2050), status=st.sampled_from(STATUSES))
def test_biden_projection_tracks_index_and_filing_status_ratios(year, status):
    anchor = 500_000 if status == "SEPARATE" else 1_000_000
    value = _value(BIDEN_PATH, status, year)
    assert value / anchor == pytest.approx(_irs_factor(year, 2024), rel=1e-12)
    assert value >= _value(BIDEN_PATH, status, year - 1)
    assert value > anchor
    joint = _value(BIDEN_PATH, "JOINT", year)
    assert _value(BIDEN_PATH, "SEPARATE", year) == pytest.approx(joint / 2, rel=1e-12)
    for same_threshold in ("SINGLE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"):
        assert _value(BIDEN_PATH, same_threshold, year) == joint


@settings(**PROPERTY_SETTINGS)
@given(case=st.sampled_from(AUTHORED_VALUES))
@example(case=(CO_PATH, "SINGLE", "2021-01-01", float("inf")))
@example(case=(PEP_PATH, "JOINT", "2018-01-01", float("inf")))
def test_uprating_preserves_authored_values(case):
    path, status, date, expected = case
    actual = get_parameter(system.parameters, f"{path}.{status}")(date)
    assert actual == expected
