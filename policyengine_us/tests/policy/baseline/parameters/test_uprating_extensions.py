"""Test unified uprating extensions through 2100."""

from policyengine_us.system import system
from policyengine_us.parameters.uprating_extensions import (
    LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS,
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
        ("CPI-U", parameters.gov.bls.cpi.cpi_u, "-02-01"),
        ("Chained CPI-U", parameters.gov.bls.cpi.c_cpi_u, "-02-01"),
        ("CPI-W", parameters.gov.bls.cpi.cpi_w, "-02-01"),
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


def test_cms_moop_per_capita_extends_to_2100():
    """Health expense input upraters should not flatten after 2035."""
    parameter = PARAMETERS.calibration.gov.hhs.cms.moop_per_capita

    assert parameter("2036-01-01") > parameter("2035-01-01")
    assert parameter("2100-01-01") > parameter("2036-01-01")


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
    taxable_uprater = "calibration.gov.irs.soi.taxable_pension_income"
    tax_exempt_uprater = "calibration.gov.irs.soi.tax_exempt_pension_income"

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
    """Every float USD input should have a resolvable non-flat 2100 uprater."""
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


def test_ssa_nawi_and_payroll_cap_extend_to_2100():
    """Test that the SSA NAWI and payroll cap do not flatten after 2035."""
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

    for year in [2036, 2040, 2050, 2100]:
        current_cap = payroll_cap(f"{year - 1}-01-01")
        expected_cap = round_social_security_payroll_cap(
            current_cap * nawi(f"{year - 2}-01-01") / nawi(f"{year - 3}-01-01")
        )
        assert payroll_cap(f"{year}-01-01") == expected_cap


def test_social_security_payroll_cap_formula_matches_known_values():
    """Test known caps against the statutory NAWI-indexing formula."""
    parameters = PARAMETERS

    payroll_cap = parameters.gov.irs.payroll.social_security.cap
    nawi = parameters.gov.ssa.nawi

    expected_2025_cap = round_social_security_payroll_cap(
        payroll_cap("2024-01-01") * nawi("2023-01-01") / nawi("2022-01-01")
    )

    assert expected_2025_cap == payroll_cap("2025-01-01")

    expected_2026_cap = round_social_security_payroll_cap(
        payroll_cap("1994-01-01") * nawi("2024-01-01") / nawi("1992-01-01")
    )

    assert expected_2026_cap == 184_500
    assert expected_2026_cap == payroll_cap("2026-01-01")


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
