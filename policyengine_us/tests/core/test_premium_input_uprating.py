"""Premium inputs follow premium series, not CMS out-of-pocket spending.

CMS defines out-of-pocket spending to exclude premiums (NHEA methodology
paper, 2024, file page 14), so no premium input uprates by
``moop_per_capita``. Each follows the series closest to what the data put in
it:

- ``health_insurance_premiums_without_medicare_part_b`` carries the CPS ASEC
  premium the person reported (``PHIP_VAL``), and
  ``other_health_insurance_premiums`` is that premium less modeled CHIP,
  Medicaid and Marketplace premiums. People with employer-sponsored coverage
  pay most of these dollars, and Microcosm's pre-tax producer moves employees'
  payroll-deducted premiums from these inputs to
  ``pre_tax_health_insurance_premiums``. All three follow CMS's
  employer-sponsored insurance (ESI) premium per enrollee, so that move leaves
  the dollars' growth unchanged.
- ``health_insurance_premiums`` holds premiums of self-employed people under 65
  without employer-sponsored coverage, who buy plans directly. It follows
  CMS's direct purchase premium per enrollee.
- ``long_term_health_insurance_premiums``: no dataset fills it and no CMS
  series measures long-term care insurance premiums. 26 U.S.C. 213(d)(10)(B)
  indexes the deductible limits on them by the medical care component of the
  CPI, so it follows CPI-U medical care.
- ``medicare_part_b_premiums_reported`` follows the Part B standard premium:
  a premium with any income-related adjustment is a fixed multiple of it
  (42 U.S.C. 1395r(i)(3)).

These tests read only the parameter tree. Engine uprating of the inputs is
covered in ``tests/microsimulation/test_premium_input_microsim_uprating.py``.

Invariants:

1. Transcription: each series equals its published source figure for figure,
   and is consistent with the source's own components within rounding: CMS
   direct purchase spending over enrollment; CBO's medical care CPI levels
   against its percentage changes and against BLS; the Part B premium against
   half the aged actuarial rate plus the repayment add-on.
2. Employee share: ESI spending less employer contributions, per ESI
   enrollee, grows with the ESI index, so one index serves employees'
   premiums whether paid pre-tax or post-tax.
3. Move neutrality: every input that holds employees' shares of ESI premiums
   names the same series.
4. Agreement: the Part B series equals the model's Part B premium parameter
   in every year that parameter holds.
5. Bounds and order: each index is positive in every year, and strictly
   increasing from its last published dip (direct purchase from 2020, Part B
   from 2023, medical care CPI throughout) to 2100.
6. Extension rule: past its source's last year, each index grows at its last
   published one-year rate to 2100 and holds its 2100 value after.
7. No premium input follows out-of-pocket spending.
"""

from decimal import ROUND_HALF_UP, Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

MOOP = "calibration.gov.hhs.cms.moop_per_capita"
ESI = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
DIRECT_PURCHASE = "calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee"
MEDICAL_CPI = "gov.bls.cpi.cpi_u_medical_care"
PART_B = "calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee"
SERIES = {
    "employer_sponsored_insurance_premiums": ESI,
    "pre_tax_health_insurance_premiums": ESI,
    "health_insurance_premiums_without_medicare_part_b": ESI,
    "other_health_insurance_premiums": ESI,
    "health_insurance_premiums": DIRECT_PURCHASE,
    "long_term_health_insurance_premiums": MEDICAL_CPI,
    "medicare_part_b_premiums_reported": PART_B,
}
EMPLOYEE_ESI_INPUTS = (
    "pre_tax_health_insurance_premiums",
    "health_insurance_premiums_without_medicare_part_b",
    "other_health_insurance_premiums",
)
END_YEAR = 2100
# First year, last published year and the year from which each index rises
# every year.
SPANS = {
    DIRECT_PURCHASE: (2013, 2034, 2020),
    MEDICAL_CPI: (2015, 2036, 2015),
    PART_B: (2013, 2035, 2023),
}


def _index(path, year):
    return get_parameter(system.parameters, path)(f"{year}-01-01")


# Wiring.


@pytest.mark.parametrize("variable, series", sorted(SERIES.items()))
def test_premium_input_follows_its_premium_series(variable, series):
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


def test_inputs_holding_employee_esi_shares_follow_one_series():
    """Microcosm's pre-tax producer moves an employee's payroll-deducted
    premium out of the reported premium inputs into the pre-tax input. One
    series for all of them keeps that move from changing the dollars' growth."""
    assert {system.variables[name].uprating for name in EMPLOYEE_ESI_INPUTS} == {ESI}


# Employer-sponsored insurance: CMS NHE projections tables (2025-2034 release,
# https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70), Table 17 ESI spending and enrollment,
# and Table 16 employer contributions to private health insurance premiums by
# private business, the federal government and state and local governments.
ESI_SPENDING_BILLIONS = {2024: 1_429.1, 2026: 1_650.5, 2034: 2_343.1}
ESI_ENROLLMENT_MILLIONS = {2024: 178.6, 2026: 179.8, 2034: 178.5}
EMPLOYER_CONTRIBUTIONS_BILLIONS = {
    2024: 753 + 47 + 247,
    2026: 865 + 56 + 288,
    2034: 1_207 + 82 + 429,
}


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


# Direct purchase: the same tables, Table 17 "Direct Purchase" rows.
DIRECT_PURCHASE_YEARS = range(2013, 2035)
DIRECT_PURCHASE_SPENDING_PER_ENROLLEE = dict(
    zip(
        DIRECT_PURCHASE_YEARS,
        (
            *(2_263, 3_134, 3_454, 3_695, 4_175, 4_831, 4_812, 4_791, 4_979),
            *(5_149, 5_458, 5_871, 5_994, 6_969, 7_174, 7_456, 7_752, 8_115),
            *(8_364, 8_743, 9_158, 9_589),
        ),
    )
)
DIRECT_PURCHASE_SPENDING_BILLIONS = dict(
    zip(
        DIRECT_PURCHASE_YEARS,
        (
            *(51.1, 81.3, 101.4, 110.2, 115.7, 129.7, 129.0, 131.5, 142.2),
            *(154.7, 177.6, 215.5, 229.3, 240.6, 246.2, 246.8, 256.7, 270.3),
            *(288.6, 303.5, 319.0, 335.3),
        ),
    )
)
DIRECT_PURCHASE_ENROLLMENT_MILLIONS = dict(
    zip(
        DIRECT_PURCHASE_YEARS,
        (
            *(22.6, 26.0, 29.4, 29.8, 27.7, 26.8, 26.8, 27.5, 28.6, 30.0),
            *(32.5, 36.7, 38.3, 34.5, 34.3, 33.1, 33.1, 33.3, 34.5, 34.7),
            *(34.8, 35.0),
        ),
    )
)


@pytest.mark.parametrize("year", DIRECT_PURCHASE_YEARS)
def test_direct_purchase_index_is_table_17_spending_per_enrollee(year):
    assert _index(DIRECT_PURCHASE, year) == DIRECT_PURCHASE_SPENDING_PER_ENROLLEE[year]


@pytest.mark.parametrize("year", DIRECT_PURCHASE_YEARS)
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


def test_direct_purchase_index_dips_where_cms_reports_it():
    """CMS's direct purchase premium per enrollee falls in 2019 and 2020;
    the parameter keeps CMS's figures rather than smoothing them."""
    assert _index(DIRECT_PURCHASE, 2019) < _index(DIRECT_PURCHASE, 2018)
    assert _index(DIRECT_PURCHASE, 2020) < _index(DIRECT_PURCHASE, 2019)


# CPI-U medical care: BLS annual means to 2022 and CBO's February 2026
# Economic Projections, sheet "2. Calendar Year", row 59 (level, 1982-84=100)
# and row 60 (percentage change, annual rate) from 2023.
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


@pytest.mark.parametrize("year", sorted(CBO_MEDICAL_CPI))
def test_medical_cpi_is_cbo_calendar_year_series(year):
    assert _index(MEDICAL_CPI, year) == CBO_MEDICAL_CPI[year]


@pytest.mark.parametrize("year", sorted(CBO_MEDICAL_CPI_PERCENT_CHANGE))
def test_medical_cpi_levels_match_cbo_percent_changes(year):
    """CBO publishes levels and percentage changes to three decimals, so each
    change agrees with the levels within rounding. The 2023 change also
    checks the BLS 2022 value that precedes CBO's series."""
    change = 100 * (_index(MEDICAL_CPI, year) / _index(MEDICAL_CPI, year - 1) - 1)
    assert change == pytest.approx(CBO_MEDICAL_CPI_PERCENT_CHANGE[year], abs=0.001)


@pytest.mark.parametrize("year", [2022, 2023, 2024])
def test_medical_cpi_matches_bls_where_bls_has_a_full_year(year):
    assert _index(MEDICAL_CPI, year) == pytest.approx(
        BLS_MEDICAL_CPI_ANNUAL_MEAN[year], abs=0.005
    )


# Part B standard monthly premium: 2026 Medicare Trustees Report, Table III.C2
# (file pages 89-90, 2013-2026, with the aged monthly actuarial rate) and
# Table V.E2 (file page 213, intermediate estimates for 2027-2035).
PART_B_STANDARD_PREMIUM = dict(
    zip(
        range(2013, 2036),
        (
            *(104.9, 104.9, 104.9, 121.8, 134.0, 134.0, 135.5, 144.6, 148.5),
            *(170.1, 164.9, 174.7, 185.0, 202.9, 209.5, 224.5, 238.5, 255.5),
            *(272.1, 290.2, 313.6, 338.5, 360.6),
        ),
    )
)
PART_B_AGED_ACTUARIAL_RATE = dict(
    zip(
        range(2013, 2027),
        (
            *("209.80", "209.80", "209.80", "237.60", "261.90", "261.90"),
            *("264.90", "283.20", "291.00", "334.20", "323.70", "343.40"),
            *("368.10", "405.40"),
        ),
    )
)
# 42 U.S.C. 1395r(a)(6): the add-on that repays the 2016 premium relief, $3.00
# through 2024, $0.90 in 2025 and $0.20 in 2026 (2026 Trustees Report,
# footnote on file page 88).
PART_B_REPAYMENT_ADD_ON = {
    **{year: "0" for year in range(2013, 2016)},
    **{year: "3.00" for year in range(2016, 2025)},
    2025: "0.90",
    2026: "0.20",
}


@pytest.mark.parametrize("year", sorted(PART_B_STANDARD_PREMIUM))
def test_part_b_index_is_the_trustees_standard_premium(year):
    assert _index(PART_B, year) == PART_B_STANDARD_PREMIUM[year]


@pytest.mark.parametrize("year", sorted(PART_B_AGED_ACTUARIAL_RATE))
def test_part_b_premium_is_half_the_aged_actuarial_rate_plus_the_add_on(year):
    """42 U.S.C. 1395r(a)(3) sets the premium at 50% of the aged actuarial
    rate, (a)(6) adds the repayment amount, and (c) rounds to the nearest
    multiple of 10 cents."""
    premium = (
        Decimal(PART_B_AGED_ACTUARIAL_RATE[year]) / 2
        + Decimal(PART_B_REPAYMENT_ADD_ON[year])
    ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    assert float(premium) == _index(PART_B, year)


@pytest.mark.parametrize("year", range(2021, 2027))
def test_part_b_index_agrees_with_the_model_part_b_premium(year):
    """``gov.hhs.medicare.part_b.base_premium`` computes modeled Part B
    premiums from the same announced amounts."""
    base_premium = get_parameter(
        system.parameters, "gov.hhs.medicare.part_b.base_premium"
    )
    assert _index(PART_B, year) == base_premium(f"{year}-01-01")


# Every index.


@given(
    st.sampled_from((ESI, DIRECT_PURCHASE, MEDICAL_CPI, PART_B)),
    st.integers(2015, END_YEAR + 50),
)
def test_each_index_is_positive(path, year):
    assert _index(path, year) > 0


@given(st.sampled_from(sorted(SPANS)), st.integers(0, END_YEAR), st.integers(1, 99))
def test_each_index_strictly_increases_after_its_last_dip(path, offset, gap):
    _, _, rises_from = SPANS[path]
    year = rises_from + offset % (END_YEAR - rises_from)
    later = min(year + gap, END_YEAR)
    assert _index(path, year) < _index(path, later)


@given(st.sampled_from(sorted(SPANS)), st.integers(0, END_YEAR))
def test_each_extension_holds_the_last_published_growth_rate(path, offset):
    _, last, _ = SPANS[path]
    year = last + 1 + offset % (END_YEAR - last)
    last_growth = _index(path, last) / _index(path, last - 1)
    growth = _index(path, year) / _index(path, year - 1)
    assert growth == pytest.approx(last_growth, rel=1e-12)


@pytest.mark.parametrize(
    "path, last_growth",
    [
        (DIRECT_PURCHASE, 9_589 / 9_158),
        (MEDICAL_CPI, 813.07 / 788.642),
        (PART_B, 360.6 / 338.5),
    ],
)
def test_last_published_growth_rates(path, last_growth):
    _, last, _ = SPANS[path]
    assert _index(path, last) / _index(path, last - 1) == pytest.approx(
        last_growth, rel=1e-12
    )


@given(
    st.sampled_from((ESI, DIRECT_PURCHASE, MEDICAL_CPI, PART_B)),
    st.integers(END_YEAR, END_YEAR + 100),
)
def test_each_index_holds_its_2100_value_after_2100(path, year):
    assert _index(path, year) == _index(path, END_YEAR)
