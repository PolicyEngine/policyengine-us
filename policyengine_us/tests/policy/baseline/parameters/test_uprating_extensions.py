"""Test unified uprating extensions through 2100."""

import datetime
import math
from pathlib import Path
from types import SimpleNamespace
import pytest
import yaml

from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.variables.variable import QuantityType

from policyengine_us.system import system
from policyengine_us.tools.default_uprating import NO_DEFAULT_UPRATING_VARIABLES
from policyengine_us.tools.per_capita_uprating import per_capita_path
from policyengine_us.parameters.uprating_extensions import (
    DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES,
    EDUCATOR_EXPENSE_CAP_STATUTORY_BASE,
    LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS,
    extend_dependent_standard_deduction_parameters,
    extend_educator_expense_cap,
    get_irs_cola,
    get_irs_cola_denominator,
    round_social_security_amount,
    round_social_security_payroll_cap,
)


PARAMETERS = system.parameters


def test_all_uprating_factors_extend_to_2100():
    """Test that all uprating factors extend through 2100 with consistent growth rates."""
    parameters = PARAMETERS

    # Define all uprating parameters to test with their specific periods
    uprating_params = [
        ("IRS", parameters.gov.irs.uprating, "-01-01"),
        ("SNAP", parameters.gov.usda.snap.uprating, "-10-01"),
        ("SSA", parameters.gov.ssa.uprating, "-01-01"),
        ("HHS", parameters.gov.hhs.uprating, "-01-01"),
        ("HHS poverty guidelines", parameters.gov.hhs.fpg_uprating, "-01-01"),
        ("CPI-U", parameters.gov.bls.cpi.cpi_u, "-02-01"),
        ("Chained CPI-U", parameters.gov.bls.cpi.c_cpi_u, "-02-01"),
        ("CPI-W", parameters.gov.bls.cpi.cpi_w, "-02-01"),
        (
            "CMS Medicare spending per enrollee",
            parameters.calibration.gov.hhs.medicare.per_capita_cost,
            "-01-01",
        ),
    ]

    for name, param, date_suffix in uprating_params:
        # Test that values exist and are positive for future years
        test_years = [2035, 2050, 2075, 2100]
        values = []

        for year in test_years:
            value = param(f"{year}{date_suffix}")
            assert value > 0, f"No positive {name} uprating value for year {year}"
            values.append(value)

        # Test that values are monotonically increasing
        for i in range(1, len(values)):
            assert values[i] > values[i - 1], (
                f"{name} uprating should increase from {test_years[i - 1]} to {test_years[i]}"
            )

        # Test that growth is consistent in the extended period
        # Use years after the projection period ends
        year1, year2, year3 = 2040, 2041, 2042
        val1 = param(f"{year1}{date_suffix}")
        val2 = param(f"{year2}{date_suffix}")
        val3 = param(f"{year3}{date_suffix}")

        growth_rate_1 = val2 / val1
        growth_rate_2 = val3 / val2

        # Growth rates should be approximately equal (within 0.1%)
        assert abs(growth_rate_1 - growth_rate_2) < 0.001, (
            f"{name} growth rate should be consistent: {growth_rate_1:.5f} vs {growth_rate_2:.5f}"
        )


def test_cbo_income_by_source_anchors_extend_to_2100():
    """CBO income-source anchors should not flatten after the budget window."""
    income_by_source = PARAMETERS.calibration.gov.cbo.income_by_source

    for parameter_name in LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS:
        parameter = getattr(income_by_source, parameter_name)
        values = [parameter(f"{year}-01-01") for year in [2036, 2050, 2075, 2100]]

        for value in values:
            assert value > 0, f"{parameter_name} should stay positive"
        for previous, current in zip(values, values[1:]):
            assert current != previous, f"{parameter_name} should extend after 2036"


def test_gross_social_security_benefits_extend_to_2100():
    """Gross Social Security benefits should not flatten after the budget window."""
    social_security = PARAMETERS.calibration.gov.cbo.social_security

    assert social_security("2037-01-01") > social_security("2036-01-01")
    assert social_security("2100-01-01") > social_security("2036-01-01")


def test_soi_social_security_uses_gross_benefit_uprater():
    """Social Security benefit inputs should age with gross benefits."""
    soi_social_security = PARAMETERS.calibration.gov.irs.soi.social_security
    gross_social_security = PARAMETERS.calibration.gov.cbo.social_security

    assert (
        soi_social_security.metadata["uprating"]
        == "calibration.gov.cbo.social_security"
    )

    for year in [2037, 2050, 2075, 2100]:
        previous_year = year - 1
        soi_growth = soi_social_security(f"{year}-01-01") / soi_social_security(
            f"{previous_year}-01-01"
        )
        gross_growth = gross_social_security(f"{year}-01-01") / gross_social_security(
            f"{previous_year}-01-01"
        )

        assert soi_growth == pytest.approx(gross_growth)


def test_social_security_benefit_inputs_use_gross_benefit_uprater():
    """Reported Social Security benefit inputs should share the gross-benefit path."""
    for variable_name in [
        "social_security_retirement",
        "social_security_disability",
        "social_security_survivors",
        "social_security_dependents",
    ]:
        assert system.variables[
            f"{variable_name}_reported"
        ].uprating == per_capita_path("calibration.gov.irs.soi.social_security")
        assert system.variables[variable_name].uprating is None


def test_cms_moop_per_capita_extends_to_2100():
    """Health expense input upraters keep growing after CMS's 2034
    projection, at the 2033-2034 growth rate, then hold the 2100 value."""
    parameter = PARAMETERS.calibration.gov.hhs.cms.moop_per_capita
    last_growth = parameter("2034-01-01") / parameter("2033-01-01")

    assert parameter("2034-01-01") == 2_512
    assert last_growth == pytest.approx(2_512 / 2_412, rel=1e-12)
    for year in [2035, 2036, 2050, 2100]:
        growth = parameter(f"{year}-01-01") / parameter(f"{year - 1}-01-01")
        assert growth == pytest.approx(last_growth, rel=1e-12)
    assert parameter("2150-01-01") == parameter("2100-01-01")


def test_cms_esi_premium_per_enrollee_holds_last_projected_growth_rate():
    """Employer plan premium inputs keep growing after CMS's 2034 projection,
    at the 2033-2034 growth rate."""
    parameter = PARAMETERS.calibration.gov.hhs.cms.esi_premium_per_enrollee
    last_growth = parameter("2034-01-01") / parameter("2033-01-01")

    assert parameter("2034-01-01") == 13_124
    for year in [2035, 2036, 2050, 2100]:
        growth = parameter(f"{year}-01-01") / parameter(f"{year - 1}-01-01")
        assert growth == pytest.approx(last_growth, rel=1e-12)
    assert parameter("2150-01-01") == parameter("2100-01-01")


def test_cms_direct_purchase_premium_per_enrollee_holds_last_projected_growth_rate():
    """Directly bought premium inputs keep growing after CMS's 2034
    projection, at the 2033-2034 growth rate."""
    parameter = PARAMETERS.calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee
    last_growth = parameter("2034-01-01") / parameter("2033-01-01")

    assert parameter("2034-01-01") == 9_589
    for year in [2035, 2036, 2050, 2100]:
        growth = parameter(f"{year}-01-01") / parameter(f"{year - 1}-01-01")
        assert growth == pytest.approx(last_growth, rel=1e-12)
    assert parameter("2150-01-01") == parameter("2100-01-01")


def test_medicare_part_b_premium_holds_last_projected_growth_rate():
    """Reported Part B premium inputs keep growing after the Trustees' 2035
    projection, at the 2034-2035 growth rate."""
    parameter = PARAMETERS.calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee
    last_growth = parameter("2035-01-01") / parameter("2034-01-01")

    assert parameter("2035-01-01") == 360.6
    for year in [2036, 2037, 2050, 2100]:
        growth = parameter(f"{year}-01-01") / parameter(f"{year - 1}-01-01")
        assert growth == pytest.approx(last_growth, rel=1e-12)
    assert parameter("2150-01-01") == parameter("2100-01-01")


def test_cpi_u_medical_care_holds_last_projected_growth_rate():
    """Long-term care premium inputs keep growing after CBO's 2036
    projection, at the 2035-2036 growth rate."""
    parameter = PARAMETERS.gov.bls.cpi.cpi_u_medical_care
    last_growth = parameter("2036-01-01") / parameter("2035-01-01")

    assert parameter("2036-01-01") == 813.07
    for year in [2037, 2038, 2050, 2100]:
        growth = parameter(f"{year}-01-01") / parameter(f"{year - 1}-01-01")
        assert growth == pytest.approx(last_growth, rel=1e-12)
    assert parameter("2150-01-01") == parameter("2100-01-01")


def test_soi_income_upraters_extend_without_trustees_reform():
    """SOI income upraters should inherit baseline long-run CBO extensions."""
    soi = PARAMETERS.calibration.gov.irs.soi

    for parameter_name in [
        "employment_income",
        "self_employment_income",
        "qualified_dividend_income",
        "taxable_interest_income",
        "taxable_pension_income",
        "tax_exempt_pension_income",
        "social_security",
    ]:
        parameter = getattr(soi, parameter_name)
        assert parameter("2037-01-01") > parameter("2036-01-01")
        assert parameter("2100-01-01") > parameter("2036-01-01")


def test_retirement_distribution_inputs_use_pension_upraters():
    """Retirement account components should age with pension income, not AGI."""
    taxable_uprater = per_capita_path("calibration.gov.irs.soi.taxable_pension_income")
    tax_exempt_uprater = per_capita_path(
        "calibration.gov.irs.soi.tax_exempt_pension_income"
    )

    for variable_name in [
        "csrs_retirement_pay",
        "keogh_distributions",
        "military_retirement_pay",
        "military_retirement_pay_survivors",
        "pension_survivors",
        "retirement_benefits_from_ss_exempt_employment",
        "taxable_ira_distributions",
        "taxable_401k_distributions",
        "taxable_403b_distributions",
        "taxable_federal_pension_income",
        "taxable_public_pension_income",
        "taxable_sep_distributions",
        "taxable_private_pension_income",
    ]:
        assert system.variables[variable_name].uprating == taxable_uprater

    for variable_name in [
        "tax_exempt_ira_distributions",
        "tax_exempt_401k_distributions",
        "tax_exempt_403b_distributions",
        "tax_exempt_public_pension_income",
        "tax_exempt_sep_distributions",
        "tax_exempt_private_pension_income",
    ]:
        assert system.variables[variable_name].uprating == tax_exempt_uprater


def test_float_dollar_inputs_have_long_run_upraters():
    """Every float USD input should have a resolvable non-flat 2100 uprater,
    except the stocks default_uprating.py deliberately holds at their dataset
    value."""
    missing = []
    unresolvable = []
    flat = []

    for variable in system.variables.values():
        if not (
            variable.is_input_variable()
            and variable.value_type is float
            and variable.unit == "currency-USD"
        ):
            continue
        if variable.name in NO_DEFAULT_UPRATING_VARIABLES:
            continue

        if variable.uprating is None:
            missing.append(variable.name)
            continue

        parameter = PARAMETERS
        try:
            for path_part in variable.uprating.split("."):
                parameter = getattr(parameter, path_part)
            value_2036 = float(parameter("2036-01-01"))
            value_2100 = float(parameter("2100-01-01"))
        except (AttributeError, TypeError, ValueError):
            unresolvable.append((variable.name, variable.uprating))
            continue

        if value_2036 == value_2100:
            flat.append((variable.name, variable.uprating))

    assert missing == []
    assert unresolvable == []
    assert flat == []


def test_held_balances_are_unuprated_stocks():
    """Each variable default_uprating.py holds at its dataset value exists,
    declares no uprater and is a stock, so the exemption cannot go stale."""
    for name in NO_DEFAULT_UPRATING_VARIABLES:
        variable = system.variables[name]
        assert variable.uprating is None, name
        assert variable.quantity_type == QuantityType.STOCK, name


def test_ssa_nawi_and_payroll_cap_extend_to_2100():
    """Test that the SSA NAWI and payroll cap do not flatten after 2036."""
    parameters = PARAMETERS

    nawi = parameters.gov.ssa.nawi
    payroll_cap = parameters.gov.irs.payroll.social_security.cap

    test_years = [2035, 2050, 2075, 2100]
    nawi_values = [nawi(f"{year}-01-01") for year in test_years]
    cap_values = [payroll_cap(f"{year}-01-01") for year in test_years]

    for i in range(1, len(test_years)):
        assert nawi_values[i] > nawi_values[i - 1], (
            f"NAWI should increase from {test_years[i - 1]} to {test_years[i]}"
        )
        assert cap_values[i] > cap_values[i - 1], (
            f"Payroll cap should increase from {test_years[i - 1]} to {test_years[i]}"
        )

    # 42 U.S.C. 430(b): fixed 1994 base, never below the prior year's base.
    for year in [2037, 2040, 2050, 2073, 2100]:
        expected_cap = max(
            payroll_cap(f"{year - 1}-01-01"),
            round_social_security_payroll_cap(
                payroll_cap("1994-01-01")
                * nawi(f"{year - 2}-01-01")
                / nawi("1992-01-01")
            ),
        )
        assert payroll_cap(f"{year}-01-01") == expected_cap


def test_social_security_payroll_cap_formula_matches_known_values():
    """Test known caps against the statutory NAWI-indexing formula."""
    parameters = PARAMETERS

    payroll_cap = parameters.gov.irs.payroll.social_security.cap
    nawi = parameters.gov.ssa.nawi

    expected_2025_cap = round_social_security_payroll_cap(
        payroll_cap("1994-01-01") * nawi("2023-01-01") / nawi("1992-01-01")
    )

    assert expected_2025_cap == payroll_cap("2025-01-01")

    expected_2026_cap = round_social_security_payroll_cap(
        payroll_cap("1994-01-01") * nawi("2024-01-01") / nawi("1992-01-01")
    )

    assert expected_2026_cap == 184_500
    assert expected_2026_cap == payroll_cap("2026-01-01")

    expected_2027_cap = round_social_security_payroll_cap(
        payroll_cap("1994-01-01") * nawi("2025-01-01") / nawi("1992-01-01")
    )

    assert expected_2027_cap == 192_300
    assert expected_2027_cap == payroll_cap("2027-01-01")


def test_social_security_payroll_cap_rounds_150_ties_up():
    """42 U.S.C. 430(b): a multiple of $150 (but not of $300) rounds up."""
    assert round_social_security_payroll_cap(60_450) == 60_600
    assert round_social_security_payroll_cap(60_150) == 60_300
    assert round_social_security_payroll_cap(60_449.99) == 60_300


def test_social_security_parameters_include_latest_official_2026_values():
    """Test announced 2026 SSA values before forecasts resume."""
    parameters = PARAMETERS

    assert parameters.gov.ssa.uprating("2025-01-01") == 308.729
    assert parameters.gov.ssa.uprating("2026-01-01") == 317.265
    assert parameters.gov.ssa.social_security.wage_base("2026-01-01") == 184_500
    assert parameters.gov.ssa.sga.non_blind("2026-01-01") == 1_690
    assert parameters.gov.ssa.sga.blind("2026-01-01") == 2_830
    assert (
        parameters.gov.ssa.social_security.quarters_of_coverage_threshold("2026-01-01")
        == 1_890
    )
    assert (
        parameters.gov.ssa.social_security.earnings_test.exempt_amount_under_fra(
            "2026-01-01"
        )
        == 24_480
    )
    assert (
        parameters.gov.ssa.social_security.earnings_test.exempt_amount_year_of_fra(
            "2026-01-01"
        )
        == 65_160
    )

    pia = parameters.gov.ssa.social_security.pia.formula_factors("2026-01-01")
    assert pia.thresholds[1] == 1_286
    assert pia.thresholds[2] == 7_749


def test_social_security_parameters_include_latest_official_2027_values():
    """Test announced 2027 SSA values, including those the extension derives from NAWI."""
    parameters = PARAMETERS
    ssa = parameters.gov.ssa
    social_security = ssa.social_security

    # 3.6% COLA: 2026Q3 CPI-W average over the 2025Q3 average.
    assert ssa.uprating("2027-01-01") == 328.746
    assert round(ssa.uprating("2027-01-01") / ssa.uprating("2026-01-01") - 1, 3) == (
        0.036
    )
    assert ssa.ssi.amount.individual("2027-01-01") == 1_029
    assert ssa.ssi.amount.couple("2027-01-01") == 1_544
    student = ssa.ssi.income.exclusions.blind_or_disabled_working_student
    assert student.amount("2027-01-01") == 2_500
    assert student.cap("2027-01-01") == 10_080

    assert parameters.gov.irs.payroll.social_security.cap("2027-01-01") == 192_300
    assert social_security.wage_base("2027-01-01") == 192_300
    assert social_security.quarters_of_coverage_threshold("2027-01-01") == 1_970
    assert social_security.earnings_test.exempt_amount_under_fra("2027-01-01") == (
        25_560
    )
    assert social_security.earnings_test.exempt_amount_year_of_fra("2027-01-01") == (
        67_920
    )
    assert ssa.sga.non_blind("2027-01-01") == 1_770
    assert ssa.sga.blind("2027-01-01") == 2_950

    # SSA's published 2025 AWI sets the 2027 PIA bend points.
    assert ssa.nawi("2025-01-01") == 72_800.33
    pia = social_security.pia.formula_factors("2027-01-01")
    assert pia.thresholds[1] == 1_340
    assert pia.thresholds[2] == 8_077


# CBO February 2026 projections, from US-CBO/cbo-data at 284a956, whose CSVs
# equal the workbook rows: quarterly_2026-02.csv and calendar_2026-02.csv
# (cpiu and chained_cpiu; Economic Projections sheets "1. Quarterly", row 53,
# and "2. Calendar Year", rows 53 and 57) and annual_cy_2026-02.csv
# (tp_ss_max_earnings; Tax Parameters sheet "1. Tax Parameters", row 155).
CBO_2026_02_QUARTERLY_CPI_U = {
    "2026Q2": 330.708,
    "2026Q3": 332.976,
    "2026Q4": 335.132,
    "2027Q1": 337.213,
    "2027Q2": 339.250,
    "2027Q3": 341.281,
    "2027Q4": 343.298,
    "2028Q1": 345.305,
    "2028Q2": 347.303,
    "2028Q3": 349.291,
    "2028Q4": 351.280,
    "2029Q1": 353.269,
    "2029Q2": 355.262,
    "2029Q3": 357.260,
    "2029Q4": 359.265,
    "2030Q1": 361.279,
    "2030Q2": 363.304,
    "2030Q3": 365.340,
    "2030Q4": 367.386,
    "2031Q1": 369.444,
    "2031Q2": 371.512,
    "2031Q3": 373.591,
    "2031Q4": 375.682,
    "2032Q1": 377.784,
    "2032Q2": 379.898,
    "2032Q3": 382.024,
    "2032Q4": 384.161,
    "2033Q1": 386.310,
    "2033Q2": 388.471,
    "2033Q3": 390.644,
    "2033Q4": 392.830,
    "2034Q1": 395.027,
    "2034Q2": 397.237,
    "2034Q3": 399.460,
    "2034Q4": 401.695,
    "2035Q1": 403.943,
    "2035Q2": 406.203,
    "2035Q3": 408.476,
    "2035Q4": 410.762,
    "2036Q1": 413.061,
    "2036Q2": 415.373,
    "2036Q3": 417.698,
    "2036Q4": 420.036,
}
CBO_2026_02_CALENDAR_CPI_U = {
    2025: 322.378,
    2026: 331.807,
    2027: 340.260,
    2028: 348.295,
    2029: 356.264,
    2030: 364.328,
    2031: 372.557,
    2032: 380.967,
    2033: 389.564,
    2034: 398.355,
    2035: 407.346,
    2036: 416.542,
}
CBO_2026_02_CALENDAR_C_CPI_U = {
    2027: 187.212,
    2028: 191.088,
    2029: 194.917,
    2030: 198.775,
    2031: 202.695,
    2032: 206.688,
    2033: 210.759,
    2034: 214.912,
    2035: 219.152,
    2036: 223.479,
}
CBO_2026_02_CBB = {
    2027: 191_100,
    2028: 198_000,
    2029: 205_500,
    2030: 212_700,
    2031: 219_900,
    2032: 227_100,
    2033: 234_900,
    2034: 242_400,
    2035: 250_500,
    2036: 258_600,
}

# The latest actuals that each projection grows from.
SSA_2026Q3_CPI_W = 328.746  # BLS CWUR0000SA0, July-September 2026 mean
JUNE_2026_CPI_W = 327.075  # BLS CWUR0000SA0
JUNE_2026_CPI_U = 333.952  # BLS CUUR0000SA0
NAWI_2025 = 72_800.33  # SSA AWI series
HHS_2026 = 328.4  # CBO January 2025 calendar-2026 CPI-U (328.446)
CALENDAR_2025_CPI_U = 321.943  # BLS CUUR0000SA0 annual average (11 months)


def _cbo_2026_02_projection_cases():
    quarterly = CBO_2026_02_QUARTERLY_CPI_U
    calendar = CBO_2026_02_CALENDAR_CPI_U
    cases = []
    # SSA: 2026Q3 CPI-W x CBO CPI-U Q3(Y - 1) / 2026Q3.
    for year in range(2028, 2037):
        growth = quarterly[f"{year - 1}Q3"] / quarterly["2026Q3"]
        cases.append(
            ("gov.ssa.uprating", f"{year}-01-01", SSA_2026Q3_CPI_W * growth, 3)
        )
    # SNAP: June 2026 CPI-U x CBO CPI-U Q2(Y) / 2026Q2.
    for year in range(2027, 2037):
        growth = quarterly[f"{year}Q2"] / quarterly["2026Q2"]
        cases.append(
            ("gov.usda.snap.uprating", f"{year}-10-01", JUNE_2026_CPI_U * growth, 3)
        )
    # HHS: 2026 value x CBO calendar CPI-U(Y) / calendar 2026.
    for year in range(2027, 2037):
        growth = calendar[year] / calendar[2026]
        cases.append(("gov.hhs.uprating", f"{year}-01-01", HHS_2026 * growth, 3))
    # Poverty guidelines: guideline year Y holds calendar Y - 1, the 2025
    # actual x CBO calendar CPI-U(Y - 1) / calendar 2025.
    for year in range(2027, 2038):
        growth = calendar[year - 1] / calendar[2025]
        cases.append(
            ("gov.hhs.fpg_uprating", f"{year}-01-01", CALENDAR_2025_CPI_U * growth, 3)
        )
    # CPI-W: each CBO CPI-U quarter at the June 2026 CPI-W / CPI-U ratio, at
    # the quarter's middle month.
    for quarter, cpi_u in quarterly.items():
        if quarter < "2026Q3":
            continue
        year, month = int(quarter[:4]), 3 * int(quarter[-1]) - 1
        cases.append(
            (
                "gov.bls.cpi.cpi_w",
                f"{year}-{month:02d}-01",
                cpi_u * JUNE_2026_CPI_W / JUNE_2026_CPI_U,
                3,
            )
        )
    # NAWI: SSA's 2025 AWI x CBO CBB(Y + 2) / CBB 2027.
    for year in range(2026, 2035):
        growth = CBO_2026_02_CBB[year + 2] / CBO_2026_02_CBB[2027]
        cases.append(("gov.ssa.nawi", f"{year}-01-01", NAWI_2025 * growth, 2))
    # CPI-U and chained CPI-U: CBO's calendar-year Y average at the Y-02-01
    # instant, to one decimal.
    for year in range(2027, 2037):
        cases.append(("gov.bls.cpi.cpi_u", f"{year}-02-01", calendar[year], 1))
        cases.append(
            (
                "gov.bls.cpi.c_cpi_u",
                f"{year}-02-01",
                CBO_2026_02_CALENDAR_C_CPI_U[year],
                1,
            )
        )
    return cases


CBO_2026_02_PROJECTION_CASES = _cbo_2026_02_projection_cases()


@pytest.mark.parametrize(
    "path,date,expected,decimals",
    CBO_2026_02_PROJECTION_CASES,
    ids=[f"{path}@{date}" for path, date, _, _ in CBO_2026_02_PROJECTION_CASES],
)
def test_upraters_encode_cbo_february_2026_projections(path, date, expected, decimals):
    """Each projected value applies CBO's February 2026 growth to its anchor.

    extend_parameter_values grows every year after a series' last CBO point at
    the ratio of its last two points, so these values, the last two included,
    also set the 2037-2100 path.

    A monthly BLS refresh writes observed values over projection instants (see
    get_average_for_12_months_ending_august). When it does, start the CPI-W
    cases after the last observed quarter and the CPI-U and chained CPI-U cases
    after the last observed February, and update JUNE_2026_CPI_W and
    JUNE_2026_CPI_U if the projections are re-anchored.
    """
    assert PARAMETERS.get_child(path)(date) == round(expected, decimals)


def test_projected_payroll_caps_follow_430b_through_2036():
    """2028-2036 caps apply 42 U.S.C. 430(b) to the CBO-based NAWI."""
    cap = PARAMETERS.gov.irs.payroll.social_security.cap
    nawi = PARAMETERS.gov.ssa.nawi
    for year in range(2028, 2037):
        assert cap(f"{year}-01-01") == round_social_security_payroll_cap(
            cap("1994-01-01") * nawi(f"{year - 2}-01-01") / nawi("1992-01-01")
        )
    assert cap("2036-01-01") == 260_400


def test_irs_uprating_averages_cbo_chained_cpi_u_points():
    """IRS(Y) averages chained CPI-U from August Y - 2 to July Y - 1 (#9105).

    Six months read the February Y - 2 point and six read February Y - 1.
    A BLS refresh that writes an observed February over a projection point
    changes the IRS years that read it; drop those years from the loop.
    """
    irs = PARAMETERS.gov.irs.uprating
    c_cpi_u = {
        year: round(value, 1) for year, value in CBO_2026_02_CALENDAR_C_CPI_U.items()
    }
    for year in range(2029, 2037):
        assert irs(f"{year}-01-01") == pytest.approx(
            (6 * c_cpi_u[year - 2] + 6 * c_cpi_u[year - 1]) / 12, rel=1e-12
        )


@pytest.mark.parametrize(
    "path,last_projected_year,date_suffix",
    [
        ("gov.irs.uprating", 2036, "-01-01"),
        ("gov.ssa.uprating", 2036, "-01-01"),
        ("gov.usda.snap.uprating", 2036, "-10-01"),
        ("gov.hhs.uprating", 2036, "-01-01"),
        ("gov.hhs.fpg_uprating", 2037, "-01-01"),
        ("gov.ssa.nawi", 2034, "-01-01"),
        ("gov.bls.cpi.cpi_u", 2036, "-02-01"),
        ("gov.bls.cpi.c_cpi_u", 2036, "-02-01"),
        ("gov.bls.cpi.cpi_w", 2036, "-02-01"),
    ],
)
def test_upraters_extrapolate_only_after_cbo_projections(
    path, last_projected_year, date_suffix
):
    """Each series holds its final projected growth after CBO's last year."""
    parameter = PARAMETERS.get_child(path)
    last_growth = parameter(f"{last_projected_year}{date_suffix}") / parameter(
        f"{last_projected_year - 1}{date_suffix}"
    )
    for year in [last_projected_year + 1, last_projected_year + 2, 2050, 2100]:
        growth = parameter(f"{year}{date_suffix}") / parameter(
            f"{year - 1}{date_suffix}"
        )
        assert growth == pytest.approx(last_growth, rel=1e-12)


EXTENDED_SERIES = [
    "gov.ssa.uprating",
    "gov.usda.snap.uprating",
    "gov.hhs.uprating",
    "gov.hhs.fpg_uprating",
    "gov.ssa.nawi",
    "gov.irs.payroll.social_security.cap",
    "gov.bls.cpi.cpi_u",
    "gov.bls.cpi.c_cpi_u",
    "gov.bls.cpi.cpi_w",
]


@pytest.mark.parametrize("path", EXTENDED_SERIES)
def test_extension_keeps_every_authored_value(path):
    """The extensions must not overwrite any value written in the YAML file."""
    parameter = PARAMETERS.get_child(path)
    with open(parameter.file_path) as f:
        authored = yaml.safe_load(f)["values"]
    for date, value in authored.items():
        if isinstance(value, dict):
            value = value["value"]
        instant = date.isoformat() if isinstance(date, datetime.date) else str(date)
        assert parameter(instant) == pytest.approx(value, abs=1e-9), instant


# Published four-person poverty guidelines for the 48 contiguous states.
PUBLISHED_FOUR_PERSON_FPG = {
    2022: 27_750,
    2023: 30_000,
    2024: 31_200,
    2025: 32_150,
    2026: 33_000,
}


def test_poverty_guideline_index_follows_the_9902_2_interval():
    """Guideline year Y uprates by CPI-U CY(Y-1)/CY(Y-2) (42 U.S.C. 9902(2)).

    The published guidelines are rounded, so their four-person increases
    match the index within 0.12%. Back-cast from 2022, the previous mapping
    (gov.hhs.uprating, one year ahead) missed the 2023-2026 guidelines by
    3.7% to 5.6%.
    """
    index = PARAMETERS.gov.hhs.fpg_uprating
    for year in range(2023, 2027):
        published = (
            PUBLISHED_FOUR_PERSON_FPG[year] / PUBLISHED_FOUR_PERSON_FPG[year - 1]
        )
        lagged = index(f"{year}-01-01") / index(f"{year - 1}-01-01")
        assert published == pytest.approx(lagged, rel=1.2e-3)
    # HHS's 2026 notice: a 2.63% increase from calendar 2024 to calendar 2025.
    assert index("2026-01-01") / index("2025-01-01") - 1 == pytest.approx(
        0.0263, abs=5e-5
    )


def test_projected_poverty_guidelines_uprate_with_the_lagged_index():
    """Projected guidelines grow with gov.hhs.fpg_uprating, not gov.hhs.uprating."""
    fpg = PARAMETERS.gov.hhs.fpg
    index = PARAMETERS.gov.hhs.fpg_uprating
    for year in (2027, 2030, 2036, 2050):
        growth = index(f"{year}-01-01") / index("2026-01-01")
        for node in (fpg.first_person, fpg.additional_person):
            for group in ("CONTIGUOUS_US", "AK", "HI"):
                parameter = node.get_child(group)
                assert parameter(f"{year}-01-01") == pytest.approx(
                    parameter("2026-01-01") * growth, rel=1e-9
                )


def test_social_security_wage_indexed_parameters_follow_statutory_rounding():
    """Wage-indexed benefit parameters should use lagged NAWI and statutory rounding."""
    parameters = PARAMETERS
    nawi = parameters.gov.ssa.nawi
    social_security = parameters.gov.ssa.social_security

    for year in [2027, 2036, 2037, 2050, 2100]:
        date = f"{year}-01-01"
        prior_date = f"{year - 1}-01-01"
        determination_nawi = nawi(f"{year - 2}-01-01")

        assert social_security.wage_base(
            date
        ) == parameters.gov.irs.payroll.social_security.cap(date)

        expected_qc_threshold = max(
            social_security.quarters_of_coverage_threshold(prior_date),
            round_social_security_amount(
                250 * determination_nawi / nawi("1976-01-01"),
                10,
            ),
        )
        assert (
            social_security.quarters_of_coverage_threshold(date)
            == expected_qc_threshold
        )

        expected_under_fra = max(
            social_security.earnings_test.exempt_amount_under_fra(prior_date),
            12
            * round_social_security_amount(
                670 * determination_nawi / nawi("1992-01-01"),
                10,
            ),
        )
        assert (
            social_security.earnings_test.exempt_amount_under_fra(date)
            == expected_under_fra
        )

        expected_year_of_fra = max(
            social_security.earnings_test.exempt_amount_year_of_fra(prior_date),
            12
            * round_social_security_amount(
                2_500 * determination_nawi / nawi("2000-01-01"),
                10,
            ),
        )
        assert (
            social_security.earnings_test.exempt_amount_year_of_fra(date)
            == expected_year_of_fra
        )

        pia = social_security.pia.formula_factors(date)
        assert pia.thresholds[1] == round_social_security_amount(
            180 * determination_nawi / nawi("1977-01-01"),
            1,
        )
        assert pia.thresholds[2] == round_social_security_amount(
            1_085 * determination_nawi / nawi("1977-01-01"),
            1,
        )

        expected_non_blind_sga = max(
            parameters.gov.ssa.sga.non_blind(prior_date),
            round_social_security_amount(
                700 * determination_nawi / nawi("1998-01-01"),
                10,
            ),
        )
        assert parameters.gov.ssa.sga.non_blind(date) == expected_non_blind_sga

        expected_blind_sga = max(
            parameters.gov.ssa.sga.blind(prior_date),
            round_social_security_amount(
                930 * determination_nawi / nawi("1992-01-01"),
                10,
            ),
        )
        assert parameters.gov.ssa.sga.blind(date) == expected_blind_sga


def test_uprating_growth_rates_are_reasonable():
    """Test that all uprating growth rates are within reasonable bounds."""
    parameters = PARAMETERS

    # Annual growth rates should be between 0.5% and 5% for inflation measures
    min_annual_growth = 1.005
    max_annual_growth = 1.05

    # Test all uprating parameters
    uprating_params = [
        ("IRS", parameters.gov.irs.uprating, "-01-01"),
        ("SNAP", parameters.gov.usda.snap.uprating, "-10-01"),
        ("SSA", parameters.gov.ssa.uprating, "-01-01"),
        ("HHS", parameters.gov.hhs.uprating, "-01-01"),
        ("HHS poverty guidelines", parameters.gov.hhs.fpg_uprating, "-01-01"),
        ("CPI-U", parameters.gov.bls.cpi.cpi_u, "-02-01"),
        ("Chained CPI-U", parameters.gov.bls.cpi.c_cpi_u, "-02-01"),
        ("CPI-W", parameters.gov.bls.cpi.cpi_w, "-02-01"),
    ]

    year1, year2 = 2050, 2051

    for name, param, date_suffix in uprating_params:
        value_year1 = param(f"{year1}{date_suffix}")
        value_year2 = param(f"{year2}{date_suffix}")
        growth_rate = value_year2 / value_year1

        assert min_annual_growth <= growth_rate <= max_annual_growth, (
            f"{name} growth rate {growth_rate:.4f} outside reasonable bounds [{min_annual_growth:.3f}, {max_annual_growth:.3f}]"
        )


def test_cpi_relationships():
    """Test that CPI indices maintain expected relationships."""
    parameters = PARAMETERS

    # Test a few years to ensure relationships are maintained
    test_years = [2040, 2060, 2080, 2100]

    for year in test_years:
        cpi_u = parameters.gov.bls.cpi.cpi_u(f"{year}-02-01")
        c_cpi_u = parameters.gov.bls.cpi.c_cpi_u(f"{year}-02-01")

        # Chained CPI-U typically grows slower than regular CPI-U
        # due to substitution effects, but not always
        # Just verify both exist and are positive
        assert cpi_u > 0, f"CPI-U should be positive in {year}"
        assert c_cpi_u > 0, f"Chained CPI-U should be positive in {year}"


def test_retirement_contribution_limits_include_latest_explicit_irs_values():
    """Retirement contribution parameters should reflect the latest published IRS anchors."""
    from policyengine_us import Microsimulation

    sim = Microsimulation()

    p2025 = sim.tax_benefit_system.parameters("2025-01-01")
    p2026 = sim.tax_benefit_system.parameters("2026-01-01")
    p2027 = sim.tax_benefit_system.parameters("2027-01-01")

    limits2025 = p2025.gov.irs.gross_income.retirement_contributions.limit
    limits2026 = p2026.gov.irs.gross_income.retirement_contributions.limit
    limits2027 = p2027.gov.irs.gross_income.retirement_contributions.limit

    assert limits2025["401k"] == 23_500
    assert limits2026["401k"] == 24_500
    assert limits2026.annual_additions == 72_000

    assert limits2027["401k"] >= limits2026["401k"]
    assert limits2027.annual_additions >= limits2026.annual_additions


def _synthetic_irs_parameters():
    """A synthetic CPI-U / C-CPI-U tree with round Sep-Aug window averages.

    The window-averaging branches themselves are pinned on synthetic series
    by the Oregon Kids' Credit COLA tests, which share the helper.
    """

    def months(start_year, start_month, end_year, end_month, level):
        year, month = start_year, start_month
        values = {}
        while (year, month) <= (end_year, end_month):
            values[f"{year}-{month:02d}-01"] = level
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        return values

    cpi_u = {
        **months(1996, 9, 1997, 8, 100),
        **months(2015, 9, 2016, 8, 200),
    }
    c_cpi_u = {
        **months(2015, 9, 2016, 8, 150),
        **months(2019, 9, 2020, 8, 60),
        # Monthly observations end in August 2030; later years hold annual
        # projection points at February instants.
        **months(2029, 9, 2030, 8, 180),
        "2032-02-01": 195,
    }
    cpi = SimpleNamespace(
        cpi_u=Parameter("cpi_u", data=cpi_u),
        c_cpi_u=Parameter("c_cpi_u", data=c_cpi_u),
    )
    return SimpleNamespace(gov=SimpleNamespace(bls=SimpleNamespace(cpi=cpi)))


def test_irs_cola_follows_1f3_on_a_synthetic_index():
    """COLA = C-CPI-U(prior year) / (CPI(base) x C-CPI-U(2016) / CPI(2016)) - 1."""
    parameters = _synthetic_irs_parameters()
    # CPI-U averages 100 over Sep 1996-Aug 1997 and 200 over Sep 2015-Aug
    # 2016; C-CPI-U averages 150 over Sep 2015-Aug 2016: 100 x 150 / 200 = 75.
    assert get_irs_cola_denominator(parameters, 1997) == pytest.approx(75)
    # Tax year 2031 reads the fully observed Sep 2029-Aug 2030 window (180).
    assert get_irs_cola(parameters, 2031, 1997) == pytest.approx(180 / 75 - 1)
    # Tax year 2033 has no observed month and reads the 2032 projection point.
    assert get_irs_cola(parameters, 2033, 1997) == pytest.approx(195 / 75 - 1)
    # "The percentage (if any)": the Sep 2019-Aug 2020 window (60) is below
    # the denominator, so the tax year 2021 COLA is zero, not negative.
    assert get_irs_cola(parameters, 2021, 1997) == 0


def test_irs_cola_denominator_uses_2016_ratio_for_pre_2017_base_years():
    """1(f)(3)(A)(ii) and (B): CPI(base year) x C-CPI-U(2016) / CPI(2016)."""
    # CPI-U Sep-Aug averages: 1986-87 111.983, 1996-97 159.492, 2015-16 238.649.
    assert get_irs_cola_denominator(PARAMETERS, 1997) == pytest.approx(
        1_913.9 / 12 * 135.993 / 238.649
    )
    assert get_irs_cola_denominator(PARAMETERS, 1987) == pytest.approx(
        1_343.8 / 12 * 135.993 / 238.649
    )
    with pytest.raises(ValueError):
        get_irs_cola_denominator(PARAMETERS, 2017)


def statutory_dependent_standard_deduction_amount(base, base_year, year):
    cola = get_irs_cola(PARAMETERS, year, base_year)
    return base + math.floor(base * cola / 50) * 50


def test_irs_cola_reproduces_published_dependent_standard_deduction_amounts():
    """The 63(c)(4) computation matches every IRS-published value, 2018-2026."""
    # As encoded in dependent/amount.yaml and additional_earned_income.yaml.
    published = {
        # year: (63(c)(5)(A) floor, 63(c)(5)(B) earned income addition)
        2018: (1_050, 350),
        2019: (1_100, 350),
        2020: (1_100, 350),
        2021: (1_100, 350),
        2022: (1_150, 400),
        2023: (1_250, 400),
        2024: (1_300, 450),
        2025: (1_350, 450),
        2026: (1_350, 450),
    }
    for year, amounts in published.items():
        computed = tuple(
            statutory_dependent_standard_deduction_amount(base, base_year, year)
            for _, base, base_year in DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES
        )
        assert computed == amounts, year


def encoded_dependent_standard_deduction_values(name):
    """The year: value pairs written in a dependent standard deduction YAML."""
    path = (
        Path(__file__).parents[4]
        / "parameters/gov/irs/deductions/standard/dependent"
        / f"{name}.yaml"
    )
    values = yaml.safe_load(path.read_text())["values"]
    return {int(str(date)[:4]): value for date, value in values.items()}


def test_dependent_standard_deduction_encoded_values_take_precedence():
    """IRS and CBO values in the YAML survive the statutory extension."""
    dependent = PARAMETERS.gov.irs.deductions.standard.dependent
    statute_differs = []
    for name, base, base_year in DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES:
        parameter = getattr(dependent, name)
        # The 0001 placeholder in additional_earned_income.yaml is not a year.
        encoded = {
            year: value
            for year, value in encoded_dependent_standard_deduction_values(name).items()
            if year >= 2018
        }
        for year, value in encoded.items():
            assert parameter(f"{year}-01-01") == value, (name, year)
            if value != statutory_dependent_standard_deduction_amount(
                base, base_year, year
            ):
                statute_differs.append((name, year))
    # The check only bites where an encoded value differs from the statutory
    # computation on the model's index: CBO's floor does in 2031 and 2034
    # (#9608).
    assert statute_differs


def test_dependent_standard_deduction_extension_starts_after_last_encoded_year():
    """A non-statutory last encoded value is kept; later years are computed."""

    def months(start_year, level):
        return {
            **{f"{start_year}-{month:02d}-01": level for month in range(9, 13)},
            **{f"{start_year + 1}-{month:02d}-01": level for month in range(1, 9)},
        }

    cpi = SimpleNamespace(
        cpi_u=Parameter(
            "cpi_u", data={**months(1986, 40), **months(1996, 100), **months(2015, 200)}
        ),
        # Monthly observations end in August 2030; 2032 holds a projection.
        c_cpi_u=Parameter(
            "c_cpi_u",
            data={**months(2015, 150), **months(2029, 190), "2032-02-01": 205},
        ),
    )
    # A node, so Parameter.update can reach a parent.
    dependent = ParameterNode(
        "dependent",
        data={
            "amount": {"values": {"2018-01-01": 1_050, "2030-01-01": 1_234}},
            "additional_earned_income": {
                "values": {"2018-01-01": 350, "2030-01-01": 999}
            },
        },
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            bls=SimpleNamespace(cpi=cpi),
            irs=SimpleNamespace(
                deductions=SimpleNamespace(
                    standard=SimpleNamespace(dependent=dependent)
                )
            ),
        )
    )
    extend_dependent_standard_deduction_parameters(parameters, 2033)

    # Encoded years keep their values, statutory or not.
    assert dependent.amount("2029-01-01") == 1_050
    assert dependent.amount("2030-01-01") == 1_234
    assert dependent.additional_earned_income("2029-01-01") == 350
    assert dependent.additional_earned_income("2030-01-01") == 999
    # Denominators: 1987 base 40 x 150 / 200 = 30; 1997 base 100 x 150 / 200 = 75.
    # 2031 reads the observed Sep 2029-Aug 2030 window (190); 2032 has no
    # observed month and no projection point of its own, so it reads 190 too.
    # Floor: $500 x (190 / 30 - 1) = $2,666.67, rounded down to $2,650.
    # Addition: $250 x (190 / 75 - 1) = $383.33, rounded down to $350.
    for year in (2031, 2032):
        assert dependent.amount(f"{year}-01-01") == 3_150
        assert dependent.additional_earned_income(f"{year}-01-01") == 600
    # 2033 reads the 2032 projection point (205).
    # Floor: $500 x (205 / 30 - 1) = $2,916.67, rounded down to $2,900.
    # Addition: $250 x (205 / 75 - 1) = $433.33, rounded down to $400.
    assert dependent.amount("2033-01-01") == 3_400
    assert dependent.additional_earned_income("2033-01-01") == 650


def test_dependent_standard_deduction_projections_follow_statute():
    """Projected years come from the statutory bases, not the rounded last value."""
    dependent = PARAMETERS.gov.irs.deductions.standard.dependent
    for name, base, base_year in DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES:
        parameter = getattr(dependent, name)
        last_explicit_year = max(encoded_dependent_standard_deduction_values(name))
        previous = parameter(f"{last_explicit_year}-01-01")
        for year in range(last_explicit_year + 1, 2101):
            value = parameter(f"{year}-01-01")
            assert value == statutory_dependent_standard_deduction_amount(
                base, base_year, year
            ), (name, year)
            assert value % 50 == 0, (name, year)
            # A tripwire at the seam between the last encoded value and the
            # statutory projection, as well as within the projection.
            assert value >= previous, (name, year)
            previous = value

    # Hand-derived anchors (derivations in basic_standard_deduction.yaml).
    # They rest on the model's CPI projection, so a CBO refresh can move the
    # 2032 and 2042 values.
    # Chaining from the rounded 2026 $450 ($450 x 1.03 = $463) would keep
    # 2027 at $450; the $250 base gives $500.
    assert dependent.additional_earned_income("2027-01-01") == 500
    assert dependent.additional_earned_income("2032-01-01") == 550
    assert dependent.additional_earned_income("2042-01-01") == 650
    assert dependent.amount("2042-01-01") == 1_900


def statutory_educator_expense_cap(year):
    """26 U.S.C. 62(d)(3): $250 plus its increase, to the nearest $50."""
    base, base_year = EDUCATOR_EXPENSE_CAP_STATUTORY_BASE
    increase = base * get_irs_cola(PARAMETERS, year, base_year)
    lower = math.floor(increase / 50) * 50
    return base + (lower if increase - lower < 25 else lower + 50)


def encoded_educator_expense_caps():
    """The year: value pairs written in the educator expense cap YAML."""
    path = (
        Path(__file__).parents[4] / "parameters/gov/irs/ald/educator_expense/cap.yaml"
    )
    values = yaml.safe_load(path.read_text())["values"]
    return {int(str(date)[:4]): value for date, value in values.items()}


def test_irs_cola_reproduces_published_educator_expense_caps():
    """The 62(d)(3) computation matches every IRS-published cap, 2016-2026."""
    encoded = encoded_educator_expense_caps()
    for year in range(2016, 2027):
        assert statutory_educator_expense_cap(year) == encoded[year], year


def test_educator_expense_cap_encoded_values_take_precedence():
    """The published caps in the YAML survive the statutory extension."""
    cap = PARAMETERS.gov.irs.ald.educator_expense.cap
    for year, value in encoded_educator_expense_caps().items():
        assert cap(f"{year}-01-01") == value, year
    # The 2002 value covers 2002-2015, before 62(d)(3) indexing.
    for year in range(2002, 2016):
        assert cap(f"{year}-01-01") == 250, year


def test_educator_expense_cap_projections_follow_statute():
    """Projected caps come from the $250 base, not the rounded 2026 $350."""
    cap = PARAMETERS.gov.irs.ald.educator_expense.cap
    last_encoded_year = max(encoded_educator_expense_caps())
    previous = cap(f"{last_encoded_year}-01-01")
    for year in range(last_encoded_year + 1, 2101):
        value = cap(f"{year}-01-01")
        assert value == statutory_educator_expense_cap(year), year
        assert value % 50 == 0, year
        assert value >= previous, year
        previous = value
    assert cap("2150-01-01") == cap("2100-01-01")

    # Hand anchors. They rest on the model's CPI projection, so a CBO refresh
    # can move them; 2031 and 2032 sit within $5 of the $125 step. The 2014
    # denominator is 134.30. The increase, $250 x the COLA, rounds to $100
    # while under $125: $89.57 in 2027, $112.80 in 2030 and $120.06 in 2031.
    # It rounds to $150 from $127.32 in 2032 to $150.03 in 2035. Chaining
    # from the rounded 2026 $350 reached $400 in 2030.
    for year in range(2027, 2032):
        assert cap(f"{year}-01-01") == 350, year
    for year in range(2032, 2036):
        assert cap(f"{year}-01-01") == 400, year


def test_educator_expense_cap_extension_rounds_the_base_increase_to_nearest_50():
    """Encoded years are kept; later years round the $250 base's increase."""

    def months(start_year, level):
        return {
            **{f"{start_year}-{month:02d}-01": level for month in range(9, 13)},
            **{f"{start_year + 1}-{month:02d}-01": level for month in range(1, 9)},
        }

    cpi = SimpleNamespace(
        cpi_u=Parameter("cpi_u", data={**months(2013, 100), **months(2015, 200)}),
        # Monthly observations end in August 2030; 2032 holds a projection.
        c_cpi_u=Parameter(
            "c_cpi_u",
            data={**months(2015, 150), **months(2029, 102), "2032-02-01": 126},
        ),
    )
    # A node, so Parameter.update can reach a parent.
    educator_expense = ParameterNode(
        "educator_expense",
        data={"cap": {"values": {"2002-01-01": 250, "2030-01-01": 999}}},
    )
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            bls=SimpleNamespace(cpi=cpi),
            irs=SimpleNamespace(ald=SimpleNamespace(educator_expense=educator_expense)),
        )
    )
    extend_educator_expense_cap(parameters, 2033)

    cap = educator_expense.cap
    # Encoded years keep their values, statutory or not.
    assert cap("2029-01-01") == 250
    assert cap("2030-01-01") == 999
    # Denominator: 2014 base 100 x 150 / 200 = 75. 2031 reads the observed
    # Sep 2029-Aug 2030 window (102); 2032 has no observed month and no
    # projection point of its own, so it reads 102 too.
    # $250 x (102 / 75 - 1) = $90, nearest to $100 (rounding down gives $50).
    for year in (2031, 2032):
        assert cap(f"{year}-01-01") == 350, year
    # 2033 reads the 2032 projection point (126).
    # $250 x (126 / 75 - 1) = $170, nearest to $150 (rounding up gives $200).
    assert cap("2033-01-01") == 400
    assert cap("2040-01-01") == 400
