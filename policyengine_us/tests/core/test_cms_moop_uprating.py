"""The CMS out-of-pocket health spending per capita series that health
expense inputs uprate by.

CMS's National Health Expenditure (NHE) projections (Table 3, 2025-2034
release) report out-of-pocket spending per capita for 2018 to 2034: historical
estimates through 2024 and projections from 2025. The parameter holds that
column. 2015 to 2017 come from CMS's historical accounts by the rule that
reproduces Table 3's 2018-2024 values, and 2035 to 2100 grow at the 2033-2034
rate.

These tests read only the parameter tree and the parameter's YAML file.

Invariants:

1. Transcription: every 2018-2034 value is Table 3's published dollar figure,
   and is consistent with the same release's out-of-pocket and national
   health expenditure aggregates (Table 3) and per-capita national health
   expenditures (Table 1) within rounding.
2. Historical rule: for 2015 to 2024, the value is per-capita national health
   expenditures times out-of-pocket spending's share of national health
   expenditures in the historical accounts, rounded to the dollar. For
   2018-2024 that reproduces Table 3, which is what licenses the rule for
   2015-2017. The historical accounts and the projections share their
   historical years, so the two sources are one vintage.
3. Markers: the YAML marks 2018-2024 as historical estimates and 2025-2034 as
   projected, as Table 3 does, and has no hand-extended years after 2034.
4. Bounds and order: the series is positive in every year. It is strictly
   increasing over 2015-2019 and 2020-2100; its one decline, 2019 to 2020
   (1,269 to 1,239), is CMS's and is intended.
5. Extension rule: each year from 2035 to 2100 grows by 2,512 / 2,412, so the
   value equals the closed form 2,512 * (2,512 / 2,412) ** (year - 2034); later
   years hold the 2100 value.
"""

import math
from pathlib import Path

import pytest
import yaml
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

MOOP = "calibration.gov.hhs.cms.moop_per_capita"
YAML_PATH = (
    Path(__file__).parents[2]
    / "parameters"
    / "calibration"
    / "gov"
    / "hhs"
    / "cms"
    / "moop_per_capita.yaml"
)
FIRST_YEAR, FIRST_TABLE_YEAR, FIRST_PROJECTED_YEAR = 2015, 2018, 2025
LAST_PROJECTED_YEAR, END_YEAR = 2034, 2100
TABLE_YEARS = range(FIRST_TABLE_YEAR, LAST_PROJECTED_YEAR + 1)
ACCOUNT_YEARS = range(FIRST_YEAR, FIRST_PROJECTED_YEAR)
# Health expense inputs that uprate by this series, as listed in
# docs-quarto/methodology/spm-poverty.qmd. Premiums follow separate series,
# covered by test_premium_input_uprating.py. HSA payroll contributions follow
# the family HSA contribution limit.
HEALTH_INPUTS = {
    "ambulance_expense",
    "er_visit_expense",
    "imaging_expense",
    "inpatient_expense",
    "lab_expense",
    "other_medical_expenses",
    "outpatient_expense",
    "over_the_counter_health_expenses",
    "physician_services_expense",
    "prescription_expense",
    "urgent_care_expense",
}

# CMS NHE projections tables
# (https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70).
# Table 3, "Per Capita Amount" block, "Out-of-Pocket Payments" column.
OOP_PER_CAPITA = dict(
    zip(
        TABLE_YEARS,
        (
            *(1_223, 1_269, 1_239, 1_372, 1_468, 1_555, 1_632),
            *(1_721, 1_826, 1_892, 1_974, 2_053, 2_139, 2_223, 2_314),
            *(2_412, 2_512),
        ),
    )
)
# Table 3, "Amount in Billions" block, "Out-of-Pocket Payments" and "Total".
OOP_BILLIONS = dict(
    zip(
        TABLE_YEARS,
        (
            *(403.0, 420.4, 412.3, 457.2, 491.9, 525.4, 556.6, 591.1, 627.9),
            *(651.8, 681.1, 710.0, 742.1, 773.6, 808.0, 845.1, 883.2),
        ),
    )
)
NHE_BILLIONS = dict(
    zip(
        TABLE_YEARS,
        (
            *(3637.7, 3805.1, 4204.3, 4376.9, 4586.6, 4925.3, 5278.6),
            *(5661.7, 6017.4, 6301.6, 6627.1, 6966.6, 7316.0, 7689.0),
            *(8074.7, 8510.9, 8970.3),
        ),
    )
)
# Table 1, "Per Capita Amount" block, "National Health Expenditures" row.
NHE_PER_CAPITA = dict(
    zip(
        range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1),
        (
            *(9_860, 10_229, 10_582, 11_042, 11_487, 12_637, 13_137),
            *(13_689, 14_580, 15_474, 16_486, 17_496, 18_295, 19_204),
            *(20_141, 21_092, 22_095, 23_124, 24_289, 25_513),
        ),
    )
)
# CMS historical accounts, NHE2024.csv rows "Out of pocket" and "Total
# National Health Expenditures", millions
# (https://www.cms.gov/files/zip/national-health-expenditures-type-service-source-funds-cy-1960-2024.zip,
# Last-Modified 2026-01-13, sha256 b6a9e267...4746).
OOP_MILLIONS = dict(
    zip(
        ACCOUNT_YEARS,
        (
            *(360_681, 375_394, 385_333, 403_033, 420_412, 412_276),
            *(457_160, 491_924, 525_424, 556_554),
        ),
    )
)
NHE_MILLIONS = dict(
    zip(
        ACCOUNT_YEARS,
        (
            *(3_177_216, 3_324_095, 3_464_208, 3_637_678, 3_805_121),
            *(4_204_311, 4_376_932, 4_586_625, 4_925_324, 5_278_588),
        ),
    )
)
EXTENSION_GROWTH = 2_512 / 2_412


def _index(year):
    return get_parameter(system.parameters, MOOP)(f"{year}-01-01")


def _round_half_up(value):
    return math.floor(value + 0.5)


def _historical_rule(year, per_capita_nhe=None):
    per_capita_nhe = NHE_PER_CAPITA[year] if per_capita_nhe is None else per_capita_nhe
    return per_capita_nhe * OOP_MILLIONS[year] / NHE_MILLIONS[year]


@pytest.mark.parametrize("year", TABLE_YEARS)
def test_index_is_table_3_out_of_pocket_per_capita(year):
    assert _index(year) == OOP_PER_CAPITA[year]


@pytest.mark.parametrize("year", TABLE_YEARS)
def test_published_values_match_aggregates_and_per_capita_nhe(year):
    """Checks three independently transcribed rows for consistency within
    publication rounding. A mistyped figure fails unless it stays inside that
    tolerance (883.3 for 2034's 883.2 would pass)."""
    # The aggregates are rounded to $0.1 billion, per-capita NHE to the
    # dollar, and the published value to the dollar.
    low = (NHE_PER_CAPITA[year] - 0.5) * (OOP_BILLIONS[year] - 0.05)
    low = low / (NHE_BILLIONS[year] + 0.05) - 0.5
    high = (NHE_PER_CAPITA[year] + 0.5) * (OOP_BILLIONS[year] + 0.05)
    high = high / (NHE_BILLIONS[year] - 0.05) + 0.5
    assert low <= OOP_PER_CAPITA[year] <= high


@pytest.mark.parametrize("year", range(FIRST_TABLE_YEAR, FIRST_PROJECTED_YEAR))
def test_historical_accounts_share_the_projections_historical_years(year):
    assert OOP_MILLIONS[year] / 1_000 == pytest.approx(OOP_BILLIONS[year], abs=0.05)
    assert NHE_MILLIONS[year] / 1_000 == pytest.approx(NHE_BILLIONS[year], abs=0.05)


@pytest.mark.parametrize("year", ACCOUNT_YEARS)
def test_values_through_2024_follow_the_historical_rule(year):
    computed = _historical_rule(year)
    assert _index(year) == _round_half_up(computed)
    if year >= FIRST_TABLE_YEAR:
        assert _round_half_up(computed) == OOP_PER_CAPITA[year]
    else:
        # For the derived years, per-capita NHE is rounded to the dollar and
        # the result rounds to the same dollar anywhere in that range. (Not
        # so for 2024, whose range straddles 1,631.5; Table 3 settles it.)
        low = _historical_rule(year, NHE_PER_CAPITA[year] - 0.5)
        high = _historical_rule(year, NHE_PER_CAPITA[year] + 0.5)
        assert _round_half_up(low) == _round_half_up(high)


def test_yaml_marks_historical_and_projected_years_as_table_3_does():
    lines = YAML_PATH.read_text().splitlines()

    def comment_before(date):
        index = next(
            i for i, line in enumerate(lines) if line.strip().startswith(f"{date}:")
        )
        return lines[index - 1].strip()

    assert comment_before(f"{FIRST_TABLE_YEAR}-01-01") == "# Historical Estimates."
    assert comment_before(f"{FIRST_PROJECTED_YEAR}-01-01") == "# Projected."

    values = yaml.safe_load(YAML_PATH.read_text())["values"]
    years = sorted(date.year for date in values)
    assert years == list(range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1))


@given(st.integers(FIRST_YEAR, END_YEAR + 100))
def test_index_is_positive(year):
    assert _index(year) > 0


@given(
    st.sampled_from([(FIRST_YEAR, 2019), (2020, END_YEAR)]),
    st.integers(0, END_YEAR - FIRST_YEAR),
    st.integers(1, END_YEAR - FIRST_YEAR),
)
def test_index_is_strictly_increasing_where_cms_is(segment, offset, gap):
    start, end = segment
    year = start + offset % (end - start)
    later = min(year + gap, end)
    assert _index(year) < _index(later)


def test_the_only_decline_is_cms_2019_to_2020():
    declines = [
        year
        for year in range(FIRST_YEAR + 1, END_YEAR + 1)
        if _index(year) < _index(year - 1)
    ]
    assert declines == [2020]
    assert (_index(2019), _index(2020)) == (1_269, 1_239)


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_extension_holds_the_last_projected_growth_rate(year):
    growth = _index(year) / _index(year - 1)
    assert growth == pytest.approx(EXTENSION_GROWTH, rel=1e-12)
    closed_form = 2_512 * EXTENSION_GROWTH ** (year - LAST_PROJECTED_YEAR)
    assert _index(year) == pytest.approx(closed_form, rel=1e-12)


@given(st.integers(END_YEAR, END_YEAR + 200))
def test_index_holds_the_2100_value_after_2100(year):
    assert _index(year) == _index(END_YEAR)


def test_health_inputs_uprate_by_the_cms_series():
    users = {
        name for name, variable in system.variables.items() if variable.uprating == MOOP
    }
    assert users == HEALTH_INPUTS
