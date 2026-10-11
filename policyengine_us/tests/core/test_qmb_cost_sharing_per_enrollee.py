"""Medicaid spending on Medicare cost sharing per Qualified Medicare Beneficiary.

``calibration.gov.hhs.medicare.savings_programs.qmb_cost_sharing_per_enrollee``
values QMB coverage of Medicare deductibles and coinsurance at what Medicaid
spends on it. Each federal fiscal year's value is national CMS-64 net
expenditure on line 17D, "Coinsurance and Deductibles", which holds "Medicare
deductibles and coinsurance required to be paid for QMBs under §1905(p)(3)"
(CMS-64.9 Base line definitions, page 18), over QMB person-years from CMS
Program Statistics (QMB only plus QMB plus, table MDCR ENROLL AB 40). Fiscal
year Y runs October Y-1 to September Y, so its person-years are 0.25 times
calendar year Y-1 plus 0.75 times calendar year Y, and its value is dated
October 1 of Y-1. ``qmb_cost_sharing`` pays a QMB a twelfth of it each month.

Invariants:

1. Transcription: each value is the line 17D total over fiscal-year QMB
   person-years, rounded to the cent, recomputed here from the published
   totals.
2. Cross-source: line 17D equals MACStats December 2024 Exhibit 17's FY 2023
   "Medicare premiums and coinsurance" column ($27,587 million) less CMS-64
   lines 17A to 17C1 for the same year.
3. Level: every value is positive and under a fifth of the fee-for-service
   Part A and Part B cost sharing that QMBs incurred per QMB person-year in
   calendar 2022, $1,139 (MedPAC and MACPAC duals data book, December 2025,
   Table 6, over the same person-years). The series is what Medicaid pays
   after states limit payment to their Medicaid rate (42 U.S.C. 1396a(n)(2)),
   not the cost sharing Medicare charges.
4. Dating: each date reads the value of the fiscal year it falls in, and every
   date after September 2024 reads the FY 2024 value.
5. Consumers: a QMB's monthly ``qmb_cost_sharing`` is the value in force that
   month over 12, other categories get zero, and a calendar year sums to nine
   twelfths of one fiscal year's value plus three twelfths of the next.
   ``msp_federal_cost`` plus ``msp_state_cost`` equals ``msp_cost`` for QMB and
   SLMB, and a full Medicaid enrollee has no separate MSP cost.
"""

from decimal import ROUND_HALF_UP, Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system

SERIES = "calibration.gov.hhs.medicare.savings_programs.qmb_cost_sharing_per_enrollee"
FIRST_FY, LAST_FY = 2015, 2024
FISCAL_YEARS = range(FIRST_FY, LAST_FY + 1)

# CMS Medicaid Financial Management Report net expenditures, Medical
# Assistance Program, "MAP - National Totals" sheet, line "Coinsurance"
# (CMS-64.9 line 17D), total computable, from financial-management-report-
# fy<YEAR>.zip on medicaid.gov.
LINE_17D = {
    2015: 964_276_592,
    2016: 1_088_990_259,
    2017: 1_044_519_254,
    2018: 1_023_074_055,
    2019: 1_036_646_026,
    2020: 1_040_603_350,
    2021: 1_046_566_216,
    2022: 1_037_693_614,
    2023: 1_118_400_599,
    2024: 1_153_227_651,
}
# FY 2023 CMS-64 lines 17A (Medicare - Part A), 17B (Medicare - Part B) and
# 17C1 (120% - 134% Of Poverty), same sheet.
FY2023_PREMIUM_LINES = (4_467_995_163, 20_740_509_880, 1_260_062_080)
# MACStats December 2024, Exhibit 17, Total row, "Medicare premiums and
# coinsurance" column, FY 2023, millions.
MACSTATS_FY2023_MEDICARE_PREMIUMS_AND_COINSURANCE = 27_587
# CMS Program Statistics, Medicare-Medicaid Enrollment, table MDCR ENROLL AB
# 40, all areas, person-years as (QMB plus, QMB only). 2014-2016 from the
# 2017 release, 2017-2024 from the 2022 and 2024 releases.
QMB_PERSON_YEARS = {
    2014: (5_188_112, 1_329_131),
    2015: (5_302_665, 1_383_012),
    2016: (5_394_679, 1_447_912),
    2017: (5_491_307.666665925, 1_520_440.750000014),
    2018: (5_612_836.249999335, 1_552_477.333333389),
    2019: (5_740_930.41666614, 1_567_420.833333381),
    2020: (5_916_824.416666307, 1_654_229.083333384),
    2021: (6_204_436.916666491, 1_708_968.916666722),
    2022: (6_424_476.916666286, 1_742_420.166666717),
    2023: (6_767_803.583332852, 1_728_500.583333357),
    2024: (6_586_884.583332959, 1_747_429.499999969),
}
# MedPAC and MACPAC, Data book: Beneficiaries dually eligible for Medicare and
# Medicaid, December 2025, Table 6: fee-for-service Part A and Part B cost
# sharing incurred in calendar 2022, billions, QMB plus and QMB only.
CY2022_QMB_FFS_COST_SHARING_INCURRED = 8.1e9 + 1.2e9


def _series(date):
    return get_parameter(system.parameters, SERIES)(date)


def _fiscal_year_value(fiscal_year):
    return _series(f"{fiscal_year - 1}-10-01")


def _fiscal_year_person_years(fiscal_year):
    previous = sum(QMB_PERSON_YEARS[fiscal_year - 1])
    current = sum(QMB_PERSON_YEARS[fiscal_year])
    return 0.25 * previous + 0.75 * current


def _expected(fiscal_year):
    ratio = LINE_17D[fiscal_year] / _fiscal_year_person_years(fiscal_year)
    return float(Decimal(ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@pytest.mark.parametrize("fiscal_year", FISCAL_YEARS)
def test_value_is_line_17d_over_qmb_person_years(fiscal_year):
    assert _fiscal_year_value(fiscal_year) == _expected(fiscal_year)


def test_line_17d_is_macstats_medicare_column_less_premium_lines():
    total = LINE_17D[2023] + sum(FY2023_PREMIUM_LINES)
    assert round(total / 1e6) == MACSTATS_FY2023_MEDICARE_PREMIUMS_AND_COINSURANCE


@pytest.mark.parametrize("fiscal_year", FISCAL_YEARS)
def test_value_is_below_cost_sharing_incurred_per_qmb(fiscal_year):
    incurred_per_qmb = CY2022_QMB_FFS_COST_SHARING_INCURRED / sum(
        QMB_PERSON_YEARS[2022]
    )
    assert 0 < _fiscal_year_value(fiscal_year) < incurred_per_qmb / 5


@given(
    st.integers(FIRST_FY, LAST_FY),
    st.integers(1, 12),
    st.integers(1, 28),
)
def test_each_date_reads_its_fiscal_year(fiscal_year, month, day):
    calendar_year = fiscal_year - 1 if month >= 10 else fiscal_year
    if calendar_year < FIRST_FY - 1 or (calendar_year, month) < (FIRST_FY - 1, 10):
        return
    date = f"{calendar_year}-{month:02d}-{day:02d}"
    assert _series(date) == _fiscal_year_value(fiscal_year)


@given(st.integers(2024, 2100), st.integers(1, 12), st.integers(1, 28))
def test_dates_after_fy_2024_hold_its_value(year, month, day):
    if year == 2024 and month < 10:
        return
    assert _series(f"{year}-{month:02d}-{day:02d}") == _fiscal_year_value(LAST_FY)


def _person_simulation(year, person):
    members = ["person"]
    return Simulation(
        situation={
            "people": {"person": person},
            "tax_units": {"tax_unit": {"members": members}},
            "spm_units": {"spm_unit": {"members": members}},
            "families": {"family": {"members": members}},
            "marital_units": {"marital_unit": {"members": members}},
            "households": {
                "household": {"members": members, "state_code": {year: "CA"}}
            },
        }
    )


CATEGORIES = ("QMB", "SLMB", "QI", "NONE")


@settings(max_examples=25, deadline=None)
@given(st.integers(2015, 2035), st.integers(1, 12), st.sampled_from(CATEGORIES))
def test_qmb_gets_a_twelfth_of_the_value_in_force(year, month, category):
    period = f"{year}-{month:02d}"
    simulation = _person_simulation(year, {"msp_category": {period: category}})
    paid = simulation.calculate("qmb_cost_sharing", period)[0]
    expected = _series(f"{period}-01") / 12 if category == "QMB" else 0
    # Variables are float32.
    assert paid == pytest.approx(expected, rel=1e-6, abs=1e-6)


@settings(max_examples=15, deadline=None)
@given(st.integers(2015, 2035))
def test_calendar_year_sums_nine_and_three_twelfths(year):
    simulation = _person_simulation(year, {"msp_category": {year: "QMB"}})
    annual = sum(
        simulation.calculate("qmb_cost_sharing", f"{year}-{month:02d}")[0]
        for month in range(1, 13)
    )
    expected = (9 * _series(f"{year}-01-01") + 3 * _series(f"{year}-10-01")) / 12
    assert annual == pytest.approx(expected, rel=1e-6)


@settings(max_examples=25, deadline=None)
@given(
    st.integers(2015, 2035),
    st.sampled_from(("QMB", "SLMB", "QI")),
    st.sampled_from(("CA", "AL", "NY", "MS", "DC")),
    st.floats(0, 6_000, allow_nan=False),
    st.floats(0, 10_000, allow_nan=False),
    st.booleans(),
)
def test_msp_cost_splits_between_federal_and_state(
    year, category, state, part_a_premium, part_b_premium, medicaid_enrolled
):
    members = ["person"]
    simulation = Simulation(
        situation={
            "people": {
                "person": {
                    "age": {year: 67},
                    "is_medicare_eligible": {year: True},
                    "medicaid_enrolled": {year: medicaid_enrolled},
                    "msp_category": {year: category},
                    "base_part_a_premium": {year: part_a_premium},
                    "base_part_b_premium": {year: part_b_premium},
                }
            },
            "tax_units": {"tax_unit": {"members": members}},
            "spm_units": {"spm_unit": {"members": members}},
            "families": {"family": {"members": members}},
            "marital_units": {"marital_unit": {"members": members}},
            "households": {
                "household": {"members": members, "state_code": {year: state}}
            },
        }
    )
    total = simulation.calculate("msp_cost", year)[0]
    federal = simulation.calculate("msp_federal_cost", year)[0]
    state_cost = simulation.calculate("msp_state_cost", year)[0]
    if medicaid_enrolled:
        assert total == federal == state_cost == 0
        return
    cost_sharing = sum(
        simulation.calculate("qmb_cost_sharing", f"{year}-{month:02d}")[0]
        for month in range(1, 13)
    )
    premiums = part_b_premium + (part_a_premium if category == "QMB" else 0)
    assert total == pytest.approx(premiums + cost_sharing, rel=1e-5, abs=0.01)
    assert federal + state_cost == pytest.approx(total, rel=1e-5, abs=0.01)
    assert 0 <= federal <= total + 0.01
    if category == "QI":
        assert state_cost == pytest.approx(0, abs=0.01)
