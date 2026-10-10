"""Test unified uprating extensions through 2100."""

import math
from pathlib import Path
from types import SimpleNamespace
import pytest
import yaml

from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.parameters.operations.propagate_parameter_metadata import (
    propagate_parameter_metadata,
)
from policyengine_core.parameters.operations.uprate_parameters import uprate_parameters

from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import per_capita_path
from policyengine_us.parameters.uprating_extensions import (
    DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES,
    EDUCATOR_EXPENSE_CAP_STATUTORY_BASE,
    LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS,
    extend_dependent_standard_deduction_parameters,
    extend_educator_expense_cap,
    get_average_for_12_months_ending_august,
    get_irs_cola,
    get_irs_cola_denominator,
    get_irs_cpi,
    round_social_security_amount,
    round_social_security_payroll_cap,
)


PARAMETERS = system.parameters


@pytest.mark.parametrize("name", ("cpi_u", "c_cpi_u"))
def test_last_published_calendar_cbo_forecast_survives_extension(name):
    source = Path(__file__).parents[4] / "parameters/gov/bls/cpi" / f"{name}.yaml"
    with source.open() as stream:
        encoded = yaml.safe_load(stream)["values"]
    date = "2035-02-01"
    published = next(value for key, value in encoded.items() if str(key) == date)
    assert getattr(PARAMETERS.gov.bls.cpi, name)(date) == published


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
        assert system.variables[variable_name].uprating == per_capita_path(
            "calibration.gov.irs.soi.social_security"
        )


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


def test_social_security_wage_indexed_parameters_follow_statutory_rounding():
    """Wage-indexed benefit parameters should use lagged NAWI and statutory rounding."""
    parameters = PARAMETERS
    nawi = parameters.gov.ssa.nawi
    social_security = parameters.gov.ssa.social_security

    for year in [2027, 2036, 2050, 2100]:
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
        # Monthly observations end in August 2030; later years hold
        # calendar-year projection points at February instants.
        **months(2029, 9, 2030, 8, 180),
        "2032-02-01": 199,
    }
    cpi = SimpleNamespace(
        cpi_u=Parameter("cpi_u", data=cpi_u),
        c_cpi_u=Parameter("c_cpi_u", data=c_cpi_u),
        # CBO's projections of the 12 months ending the August before each
        # tax year.
        tax_year_projection=SimpleNamespace(
            cpi_u=Parameter("cpi_u_projection", data={"2033-01-01": 390}),
            c_cpi_u=Parameter("c_cpi_u_projection", data={"2033-01-01": 195}),
        ),
    )
    return SimpleNamespace(gov=SimpleNamespace(bls=SimpleNamespace(cpi=cpi)))


def test_irs_window_includes_august_excludes_prior_august():
    """1(f)(6)(B) includes the ending August in the twelve-month average."""
    monthly = Parameter(
        "c_cpi_u",
        data={
            "2024-08-01": 1_000,
            **{f"2024-{month:02d}-01": 100 for month in range(9, 13)},
            **{f"2025-{month:02d}-01": 100 for month in range(1, 8)},
            "2025-08-01": 220,
        },
    )
    cpi = SimpleNamespace(
        c_cpi_u=monthly,
        tax_year_projection=SimpleNamespace(
            c_cpi_u=Parameter("projection", data={"2026-01-01": 999})
        ),
    )
    parameters = SimpleNamespace(gov=SimpleNamespace(bls=SimpleNamespace(cpi=cpi)))

    # September-July contribute 11 x 100, and the ending August 220:
    # 1,320 / 12 = 110. Including the prior August instead gives 175.
    assert get_irs_cpi(parameters, 2025) == 110


def test_tax_year_projection_is_distinct_from_calendar_year_projection():
    """Forecast windows read the dedicated tax-year series, even after a refresh."""
    parameters = _synthetic_irs_parameters()
    cpi = parameters.gov.bls.cpi
    assert cpi.c_cpi_u("2032-02-01") == 199
    assert get_irs_cpi(parameters, 2032) == 195

    # Refreshing a calendar-year forecast cannot change this tax window.
    cpi.c_cpi_u = Parameter(
        "c_cpi_u",
        data={
            **{value.instant_str: value.value for value in cpi.c_cpi_u.values_list},
            "2032-02-01": 9_999,
        },
    )
    assert get_irs_cpi(parameters, 2032) == 195
    # Refreshing the tax-year forecast changes the window itself.
    cpi.tax_year_projection.c_cpi_u = Parameter(
        "c_cpi_u_projection", data={"2033-01-01": 205}
    )
    assert get_irs_cpi(parameters, 2032) == 205


def test_missing_month_and_partial_window_completion_are_flat_estimates():
    """A missing interior month and an unobserved tail carry prior observations."""
    monthly = Parameter(
        "c_cpi_u",
        data={
            "2025-09-01": 100,
            # October has no observation, as in the 2025 BLS series.
            "2025-11-01": 120,
            "2025-12-01": 130,
            **{f"2026-{month:02d}-01": 130 + month * 10 for month in range(1, 7)},
            # Calendar-year forecasts must not fill July and August.
            "2027-02-01": 999,
        },
    )
    projection = Parameter("projection", data={"2027-01-01": 888})

    # October carries September's 100; July and August carry June's 190.
    assert get_average_for_12_months_ending_august(
        monthly, 2026, projection
    ) == pytest.approx(1_820 / 12)


def test_published_tax_parameters_survive_cpi_refresh():
    """Revised CPI cannot overwrite the IRS amounts encoded in the source YAML."""
    parameter_dir = Path(__file__).parents[4] / "parameters"
    parameters = ParameterNode(
        data={
            "gov": {
                "irs": {
                    "uprating": {"values": {"2026-01-01": 1}},
                },
            }
        }
    )
    parameters.gov.add_child("bls", ParameterNode("gov.bls", data={}))
    parameters.gov.bls.add_child("cpi", PARAMETERS.gov.bls.cpi.clone())
    irs = parameters.gov.irs
    irs.add_child("deductions", ParameterNode("gov.irs.deductions", data={}))
    irs.add_child("ald", ParameterNode("gov.irs.ald", data={}))
    irs.deductions.add_child(
        "standard",
        ParameterNode(
            "gov.irs.deductions.standard",
            directory_path=str(parameter_dir / "gov/irs/deductions/standard"),
        ),
    )
    irs.ald.add_child(
        "educator_expense",
        ParameterNode(
            "gov.irs.ald.educator_expense",
            directory_path=str(parameter_dir / "gov/irs/ald/educator_expense"),
        ),
    )
    published = [
        (parameter, value.instant_str, value.value)
        for subtree in (irs.deductions.standard, irs.ald.educator_expense)
        for parameter in subtree.get_descendants()
        if isinstance(parameter, Parameter)
        for value in parameter.values_list
    ]

    original_index = get_irs_cpi(parameters, 2025)
    cpi = parameters.gov.bls.cpi.c_cpi_u
    cpi.update(period="month:2025-08-01:1", value=2 * cpi("2025-08-01"))
    assert get_irs_cpi(parameters, 2025) != original_index
    for year in (2026, 2027):
        irs.uprating.update(
            period=f"year:{year}-01-01:1", value=get_irs_cpi(parameters, year - 1)
        )

    # Re-run the statutory extensions and ordinary metadata uprating from
    # the source amounts, rather than a tree that already contains forecasts.
    extend_dependent_standard_deduction_parameters(parameters, 2027)
    extend_educator_expense_cap(parameters, 2027)
    propagate_parameter_metadata(parameters)
    uprate_parameters(parameters)

    for parameter, date, value in published:
        assert parameter(date) == value, (parameter.name, date)
    assert irs.deductions.standard.amount.SINGLE("2026-01-01") == 16_100
    assert irs.deductions.standard.dependent.amount("2026-01-01") == 1_350
    assert (
        irs.deductions.standard.dependent.additional_earned_income("2026-01-01") == 450
    )
    assert irs.ald.educator_expense.cap("2026-01-01") == 350


def test_irs_cola_follows_1f3_on_a_synthetic_index():
    """COLA = C-CPI-U(prior year) / (CPI(base) x C-CPI-U(2016) / CPI(2016)) - 1."""
    parameters = _synthetic_irs_parameters()
    # CPI-U averages 100 over Sep 1996-Aug 1997 and 200 over Sep 2015-Aug
    # 2016; C-CPI-U averages 150 over Sep 2015-Aug 2016: 100 x 150 / 200 = 75.
    assert get_irs_cola_denominator(parameters, 1997) == pytest.approx(75)
    # Tax year 2031 reads the fully observed Sep 2029-Aug 2030 window (180).
    assert get_irs_cola(parameters, 2031, 1997) == pytest.approx(180 / 75 - 1)
    # Tax year 2033 has no observed month, so it reads CBO's tax-year
    # projection (195), not the 2032 calendar-year point (199).
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
    """IRS values in the YAML survive the statutory extension.

    Every encoded value is an IRS publication that the statute reproduces,
    so precedence for a non-statutory value is checked on the synthetic tree
    in the next test.
    """
    dependent = PARAMETERS.gov.irs.deductions.standard.dependent
    for name, _, _ in DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES:
        parameter = getattr(dependent, name)
        # The 0001 placeholder in additional_earned_income.yaml is not a year.
        encoded = {
            year: value
            for year, value in encoded_dependent_standard_deduction_values(name).items()
            if year >= 2018
        }
        for year, value in encoded.items():
            assert parameter(f"{year}-01-01") == value, (name, year)


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
        # Monthly observations end in August 2030; 2032 holds a calendar-year
        # point, which windows do not read.
        c_cpi_u=Parameter(
            "c_cpi_u",
            data={**months(2015, 150), **months(2029, 190), "2032-02-01": 211},
        ),
        # CBO's projections of the 12 months ending the August before each
        # tax year.
        tax_year_projection=SimpleNamespace(
            cpi_u=Parameter("cpi_u_projection", data={"2033-01-01": 410}),
            c_cpi_u=Parameter(
                "c_cpi_u_projection", data={"2032-01-01": 190, "2033-01-01": 205}
            ),
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
    # observed month and reads its tax-year projection, also 190.
    # Floor: $500 x (190 / 30 - 1) = $2,666.67, rounded down to $2,650.
    # Addition: $250 x (190 / 75 - 1) = $383.33, rounded down to $350.
    for year in (2031, 2032):
        assert dependent.amount(f"{year}-01-01") == 3_150
        assert dependent.additional_earned_income(f"{year}-01-01") == 600
    # 2033 reads its tax-year projection (205), not the calendar-year point.
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


def test_statute_on_the_index_reproduces_cbo_dependent_floor_projections():
    """CBO's projected floor is 63(c)(4) applied to CBO's projected index.

    CBO Tax Parameters, February 2026, sheet 1: row 68 ("Dependent filers
    (unearned)") by tax year. The model derives the floor from row 153, the
    C-CPI-U over the 12 months ending the previous August, for 2028-2036,
    and from BLS observations for 2027, so matching row 68 in every year
    checks both the index and the statute encoding.
    """
    cbo_floor = {
        2027: 1_400,
        2028: 1_450,
        2029: 1_450,
        2030: 1_500,
        2031: 1_500,
        2032: 1_550,
        2033: 1_600,
        2034: 1_600,
        2035: 1_650,
        2036: 1_700,
    }
    dependent = PARAMETERS.gov.irs.deductions.standard.dependent
    for year, amount in cbo_floor.items():
        assert dependent.amount(f"{year}-01-01") == amount, year


def test_irs_uprating_is_the_c_cpi_u_for_12_months_ending_august():
    """1(f)(6)(B): the index for tax year T averages Sep T-2 through Aug T-1."""
    uprating = PARAMETERS.gov.irs.uprating
    # CBO's actual tax year 2026 index (Tax Parameters row 153): 177.114.
    assert uprating("2026-01-01") == pytest.approx(177.114, abs=5e-4)
    # No BLS observation covers Sep 2026-Aug 2027: CBO's projection.
    assert uprating("2028-01-01") == pytest.approx(185.881)
    assert uprating("2036-01-01") == pytest.approx(217.68)


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

    # Hand anchors. They rest on the model's CPI projection (CBO's tax-year
    # C-CPI-U from 2028), so a CBO refresh can move them; 2032 sits $0.23
    # below the $125 step. The 2014 denominator is 134.30. The increase,
    # $250 x the COLA, rounds to $100 while under $125: $89.57 in 2027,
    # $110.38 in 2030 and $124.77 in 2032 (index 201.335). It rounds to $150
    # from $132.16 in 2033 (index 205.302) to $171.34 in 2038. Chaining from
    # the rounded 2026 $350 reached $400 in 2030.
    for year in range(2027, 2033):
        assert cap(f"{year}-01-01") == 350, year
    for year in range(2033, 2039):
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
        # Monthly observations end in August 2030; 2032 holds a calendar-year
        # point, which windows do not read.
        c_cpi_u=Parameter(
            "c_cpi_u",
            data={**months(2015, 150), **months(2029, 102), "2032-02-01": 999},
        ),
        # CBO's projections of the 12 months ending the August before each
        # tax year.
        tax_year_projection=SimpleNamespace(
            cpi_u=Parameter("cpi_u_projection", data={"2033-01-01": 300}),
            c_cpi_u=Parameter(
                "c_cpi_u_projection", data={"2032-01-01": 110, "2033-01-01": 126}
            ),
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
    # Sep 2029-Aug 2030 window (102).
    # $250 x (102 / 75 - 1) = $90, nearest to $100 (rounding down gives $50).
    assert cap("2031-01-01") == 350
    # 2032 has no observed month and reads its tax-year projection (110).
    # $250 x (110 / 75 - 1) = $116.67, nearest to $100.
    assert cap("2032-01-01") == 350
    # 2033 reads its tax-year projection (126), not the calendar-year point.
    # $250 x (126 / 75 - 1) = $170, nearest to $150 (rounding up gives $200).
    assert cap("2033-01-01") == 400
    assert cap("2040-01-01") == 400
