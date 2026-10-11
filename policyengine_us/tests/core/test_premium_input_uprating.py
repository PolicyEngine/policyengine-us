"""Premium inputs follow CMS premium series, not CMS out-of-pocket spending.

CMS defines out-of-pocket spending to exclude premiums (NHEA methodology
paper, 2024, file page 14), so no premium input uprates by
``moop_per_capita``. Each follows the CMS premium series closest to what the
data put in it:

- ``health_insurance_premiums_without_medicare_part_b`` carries the CPS ASEC
  premium the person reported (``PHIP_VAL``), and
  ``other_health_insurance_premiums`` is that premium less modeled CHIP,
  Medicaid and Marketplace premiums. People with employer-sponsored coverage
  pay most of these dollars, and Microcosm's pre-tax producer moves employees'
  payroll-deducted shares from these inputs to
  ``pre_tax_health_insurance_premiums``. All three follow CMS's
  employer-sponsored insurance (ESI) premium per enrollee, so that move leaves
  the dollars' growth unchanged.
- ``health_insurance_premiums`` holds premiums of self-employed people under 65
  without employer-sponsored coverage, who buy plans directly. It follows
  CMS's direct purchase premium per enrollee (Table 17).

These tests read only the parameter tree. Engine uprating of the inputs is
covered in ``tests/microsimulation/test_premium_input_microsim_uprating.py``.

Invariants:

1. Transcription: every direct purchase value is Table 17's published dollar
   figure, consistent with the same table's direct purchase spending over
   enrollment within rounding.
2. Employee share: ESI spending less employer contributions (Table 16), per
   ESI enrollee, grows with the ESI index, so one index serves employees'
   premiums whether paid pre-tax or post-tax.
3. Move neutrality: every input that holds employees' shares of ESI premiums
   names the same series.
4. Bounds and order: each index is positive in every year, and the direct
   purchase index is strictly increasing from 2020 to 2100 (CMS's series
   falls in 2019 and 2020).
5. Extension rule: each year from 2035 to 2100 grows by 9,589 / 9,158.
6. No premium input follows out-of-pocket spending.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

MOOP = "calibration.gov.hhs.cms.moop_per_capita"
ESI = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
DIRECT_PURCHASE = "calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee"
SERIES = {
    "employer_sponsored_insurance_premiums": ESI,
    "pre_tax_health_insurance_premiums": ESI,
    "health_insurance_premiums_without_medicare_part_b": ESI,
    "other_health_insurance_premiums": ESI,
    "health_insurance_premiums": DIRECT_PURCHASE,
}
EMPLOYEE_ESI_INPUTS = (
    "pre_tax_health_insurance_premiums",
    "health_insurance_premiums_without_medicare_part_b",
    "other_health_insurance_premiums",
)
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2013, 2034, 2100
YEARS = range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1)

# CMS NHE projections tables, Table 17, "Direct Purchase" rows
# (https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70).
DIRECT_PURCHASE_SPENDING_PER_ENROLLEE = dict(
    zip(
        YEARS,
        (
            *(2_263, 3_134, 3_454, 3_695, 4_175, 4_831, 4_812, 4_791, 4_979),
            *(5_149, 5_458, 5_871, 5_994, 6_969, 7_174, 7_456, 7_752, 8_115),
            *(8_364, 8_743, 9_158, 9_589),
        ),
    )
)
DIRECT_PURCHASE_SPENDING_BILLIONS = dict(
    zip(
        YEARS,
        (
            *(51.1, 81.3, 101.4, 110.2, 115.7, 129.7, 129.0, 131.5, 142.2),
            *(154.7, 177.6, 215.5, 229.3, 240.6, 246.2, 246.8, 256.7, 270.3),
            *(288.6, 303.5, 319.0, 335.3),
        ),
    )
)
DIRECT_PURCHASE_ENROLLMENT_MILLIONS = dict(
    zip(
        YEARS,
        (
            *(22.6, 26.0, 29.4, 29.8, 27.7, 26.8, 26.8, 27.5, 28.6, 30.0),
            *(32.5, 36.7, 38.3, 34.5, 34.3, 33.1, 33.1, 33.3, 34.5, 34.7),
            *(34.8, 35.0),
        ),
    )
)
# Table 17, "Employer-sponsored Insurance" spending and enrollment, and
# Table 16, employer contributions to private health insurance premiums by
# private business, the federal government and state and local governments.
ESI_SPENDING_BILLIONS = {2024: 1_429.1, 2026: 1_650.5, 2034: 2_343.1}
ESI_ENROLLMENT_MILLIONS = {2024: 178.6, 2026: 179.8, 2034: 178.5}
EMPLOYER_CONTRIBUTIONS_BILLIONS = {
    2024: 753 + 47 + 247,
    2026: 865 + 56 + 288,
    2034: 1_207 + 82 + 429,
}


def _index(path, year):
    return get_parameter(system.parameters, path)(f"{year}-01-01")


@pytest.mark.parametrize("year", YEARS)
def test_direct_purchase_index_is_table_17_spending_per_enrollee(year):
    assert _index(DIRECT_PURCHASE, year) == DIRECT_PURCHASE_SPENDING_PER_ENROLLEE[year]


@pytest.mark.parametrize("year", YEARS)
def test_direct_purchase_values_match_spending_over_enrollment(year):
    """Checks the transcribed rows against each other, so one mistyped
    spending, enrollment or per-enrollee figure fails."""
    spending = DIRECT_PURCHASE_SPENDING_BILLIONS[year]
    enrollment = DIRECT_PURCHASE_ENROLLMENT_MILLIONS[year]
    # Both components are rounded to one decimal and the published value to
    # the dollar.
    low = 1_000 * (spending - 0.05) / (enrollment + 0.05) - 0.5
    high = 1_000 * (spending + 0.05) / (enrollment - 0.05) + 0.5
    assert low <= DIRECT_PURCHASE_SPENDING_PER_ENROLLEE[year] <= high


@pytest.mark.parametrize("start, end", [(2024, 2034), (2026, 2034)])
def test_employee_contributions_per_enrollee_grow_with_the_esi_index(start, end):
    """ESI spending is premiums paid by employers and employees (NHEA
    methodology paper, file page 29), so spending less employer contributions
    is what employees, retirees and COBRA enrollees pay."""

    def employee_share(year):
        return 1 - EMPLOYER_CONTRIBUTIONS_BILLIONS[year] / ESI_SPENDING_BILLIONS[year]

    def per_enrollee(year):
        employee = ESI_SPENDING_BILLIONS[year] - EMPLOYER_CONTRIBUTIONS_BILLIONS[year]
        return employee / ESI_ENROLLMENT_MILLIONS[year]

    years = end - start
    employee_growth = (per_enrollee(end) / per_enrollee(start)) ** (1 / years)
    index_growth = (_index(ESI, end) / _index(ESI, start)) ** (1 / years)
    assert employee_growth == pytest.approx(index_growth, abs=0.001)
    # Employees pay 26.6% to 26.8% of ESI premiums in each year.
    for year in (start, end):
        assert 0.266 <= employee_share(year) <= 0.268


def test_inputs_holding_employee_esi_shares_follow_one_series():
    """Microcosm's pre-tax producer moves an employee's payroll-deducted
    premium out of the reported premium inputs into the pre-tax input. One
    series for all of them keeps that move from changing the dollars' growth."""
    assert {system.variables[name].uprating for name in EMPLOYEE_ESI_INPUTS} == {ESI}


@pytest.mark.parametrize("variable, series", sorted(SERIES.items()))
def test_premium_input_follows_its_cms_premium_series(variable, series):
    assert system.variables[variable].uprating == series


def test_no_premium_input_follows_out_of_pocket_spending():
    """CMS out-of-pocket spending excludes premium payments, so a premium
    input on it would follow a series that leaves out what it measures."""
    on_moop = sorted(
        name
        for name, variable in system.variables.items()
        if variable.uprating == MOOP and "premium" in name
    )
    assert on_moop == []


@given(
    st.sampled_from((ESI, DIRECT_PURCHASE)),
    st.integers(FIRST_YEAR, END_YEAR + 50),
)
def test_each_index_is_positive(path, year):
    assert _index(path, year) > 0


@given(st.integers(2020, END_YEAR - 1), st.integers(1, END_YEAR - 2020))
def test_direct_purchase_index_strictly_increases_from_2020(year, gap):
    later = min(year + gap, END_YEAR)
    assert _index(DIRECT_PURCHASE, year) < _index(DIRECT_PURCHASE, later)


def test_direct_purchase_index_dips_where_cms_reports_it():
    """CMS's direct purchase premium per enrollee falls in 2019 and 2020;
    the parameter keeps CMS's figures rather than smoothing them."""
    assert _index(DIRECT_PURCHASE, 2019) < _index(DIRECT_PURCHASE, 2018)
    assert _index(DIRECT_PURCHASE, 2020) < _index(DIRECT_PURCHASE, 2019)


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_direct_purchase_extension_holds_the_last_projected_growth_rate(year):
    last_growth = _index(DIRECT_PURCHASE, LAST_PROJECTED_YEAR) / _index(
        DIRECT_PURCHASE, LAST_PROJECTED_YEAR - 1
    )
    assert last_growth == pytest.approx(9_589 / 9_158, rel=1e-12)
    growth = _index(DIRECT_PURCHASE, year) / _index(DIRECT_PURCHASE, year - 1)
    assert growth == pytest.approx(last_growth, rel=1e-12)


@given(st.integers(END_YEAR, END_YEAR + 100))
def test_direct_purchase_index_holds_its_2100_value_after_2100(year):
    assert _index(DIRECT_PURCHASE, year) == _index(DIRECT_PURCHASE, END_YEAR)


# Long-term care insurance premiums: no dataset fills the input and no CMS
# series measures these premiums. 26 U.S.C. 213(d)(10)(B) indexes the
# deductible limits on them by the medical care component of the CPI, so the
# input follows CPI-U medical care.
MEDICAL_CPI = "gov.bls.cpi.cpi_u_medical_care"
MEDICAL_CPI_FIRST_YEAR, MEDICAL_CPI_LAST_PROJECTED_YEAR = 2015, 2036
# CBO, Economic Projections, February 2026, sheet "2. Calendar Year": row 59
# (level, 1982-84=100) and row 60 (percentage change, annual rate).
CBO_MEDICAL_CPI = dict(
    zip(
        range(2023, 2037),
        (
            *(549.081, 563.841, 581.279, 600.332, 617.675, 636.697, 656.371),
            *(676.782, 697.848, 719.546, 741.904, 764.927, 788.642, 813.07),
        ),
    )
)
CBO_MEDICAL_CPI_PERCENT_CHANGE = dict(
    zip(
        range(2023, 2037),
        (
            *(0.463, 2.688, 3.092, 3.277, 2.888, 3.079, 3.09, 3.109, 3.112),
            *(3.109, 3.107, 3.103, 3.1, 3.097),
        ),
    )
)
# BLS series CUUR0000SAM, mean of the 12 published monthly indexes.
BLS_MEDICAL_CPI_ANNUAL_MEAN = {2022: 546.553, 2023: 549.084, 2024: 563.841}


def test_long_term_care_premiums_follow_medical_care_prices():
    assert system.variables["long_term_health_insurance_premiums"].uprating == (
        MEDICAL_CPI
    )


@pytest.mark.parametrize("year", sorted(CBO_MEDICAL_CPI))
def test_medical_cpi_is_cbo_calendar_year_series(year):
    assert _index(MEDICAL_CPI, year) == CBO_MEDICAL_CPI[year]


@pytest.mark.parametrize("year", sorted(CBO_MEDICAL_CPI_PERCENT_CHANGE))
def test_medical_cpi_levels_match_cbo_percent_changes(year):
    """CBO publishes levels to three decimals and changes to three decimals
    of a percentage point, so each change agrees with the levels to within
    rounding. The 2023 change checks the BLS 2022 value that precedes CBO's
    series."""
    change = 100 * (_index(MEDICAL_CPI, year) / _index(MEDICAL_CPI, year - 1) - 1)
    assert change == pytest.approx(CBO_MEDICAL_CPI_PERCENT_CHANGE[year], abs=0.001)


@pytest.mark.parametrize("year", [2023, 2024])
def test_cbo_actual_medical_cpi_matches_bls(year):
    assert CBO_MEDICAL_CPI[year] == pytest.approx(
        BLS_MEDICAL_CPI_ANNUAL_MEAN[year], abs=0.005
    )


@given(
    st.integers(MEDICAL_CPI_FIRST_YEAR, END_YEAR - 1),
    st.integers(1, END_YEAR - MEDICAL_CPI_FIRST_YEAR),
)
def test_medical_cpi_is_positive_and_strictly_increasing(year, gap):
    later = min(year + gap, END_YEAR)
    assert 0 < _index(MEDICAL_CPI, year) < _index(MEDICAL_CPI, later)


@given(st.integers(MEDICAL_CPI_LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_medical_cpi_extension_holds_the_last_projected_growth_rate(year):
    growth = _index(MEDICAL_CPI, year) / _index(MEDICAL_CPI, year - 1)
    assert growth == pytest.approx(813.07 / 788.642, rel=1e-12)


@given(st.integers(END_YEAR, END_YEAR + 100))
def test_medical_cpi_holds_its_2100_value_after_2100(year):
    assert _index(MEDICAL_CPI, year) == _index(MEDICAL_CPI, END_YEAR)
