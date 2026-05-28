"""Unified script to extend all uprating factors through 2100."""

import math

from policyengine_us.model_api import *
from policyengine_core.periods import instant


LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS = (
    "adjusted_gross_income",
    "employment_income",
    "taxable_interest_and_ordinary_dividends",
    "qualified_dividend_income",
    "net_capital_gain",
    "self_employment_income",
    "taxable_pension_income",
    "taxable_social_security",
    "irs_other_income",
    "above_the_line_deductions",
)


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    """Calculate IRS CPI based on Chained CPI-U average from Sep to Aug."""
    cpi = parameters.gov.bls.cpi.c_cpi_u
    end = instant(f"{year}-08-01")
    start = end.offset(-MONTHS_IN_YEAR, MONTH)
    monthly_cpi_values = []
    for month in range(MONTHS_IN_YEAR):
        monthly_cpi_values += [cpi(start.offset(month, MONTH))]
    return sum(monthly_cpi_values) / MONTHS_IN_YEAR


def extend_parameter_values(
    parameter: Parameter,
    last_projected_year: int,
    end_year: int,
    period_month: int = 1,
    period_day: int = 1,
) -> None:
    """
    Extend a parameter's values from last_projected_year to end_year using
    the growth rate from the last two years of projections.

    Args:
        parameter: The parameter to extend
        last_projected_year: The last year with actual/projected values
        end_year: The year to extend values through
        period_month: The month for the period (default 1 for January)
        period_day: The day for the period (default 1)
    """
    # Calculate the growth rate from the last two years of projections
    date_format = f"-{period_month:02d}-{period_day:02d}"
    second_to_last_value = parameter(f"{last_projected_year - 1}{date_format}")
    last_value = parameter(f"{last_projected_year}{date_format}")
    growth_rate = last_value / second_to_last_value

    # Apply growth rate for years beyond projections
    for year in range(last_projected_year + 1, end_year + 1):
        previous_value = parameter(f"{year - 1}{date_format}")
        new_value = previous_value * growth_rate
        parameter.update(period=f"year:{year}{date_format}:1", value=new_value)

    # Set the final value for periods after the last year
    final_value = parameter(f"{end_year}{date_format}")
    parameter.update(start=instant(f"{end_year}{date_format}"), value=final_value)


def round_social_security_payroll_cap(amount: float) -> float:
    """Round a contribution and benefit base to the statutory $300 increment."""
    return round_social_security_amount(amount, 300)


def round_social_security_amount(amount: float, increment: int) -> float:
    """Round a Social Security automatic-determination amount."""
    quotient = amount / increment
    floored = math.floor(quotient)
    fractional = quotient - floored

    if fractional < 0.5:
        return floored * increment
    return (floored + 1) * increment


def extend_social_security_payroll_cap(
    parameters: ParameterNode,
    last_projected_year: int,
    end_year: int,
) -> None:
    """
    Extend the Social Security contribution and benefit base through `end_year`.

    This follows the statutory formula in 20 CFR 404.1048 using the projected
    national average wage index (NAWI), rather than extrapolating the cap
    independently.
    """
    cap = parameters.gov.irs.payroll.social_security.cap
    nawi = parameters.gov.ssa.nawi

    last_increase_determination_year = last_projected_year - 1
    if cap(f"{last_projected_year}-01-01") <= cap(f"{last_projected_year - 1}-01-01"):
        for year in range(last_projected_year - 1, 1992, -1):
            if cap(f"{year}-01-01") > cap(f"{year - 1}-01-01"):
                last_increase_determination_year = year - 1
                break

    for year in range(last_projected_year + 1, end_year + 1):
        determination_year = year - 1
        current_cap = cap(f"{determination_year}-01-01")
        numerator = nawi(f"{determination_year - 1}-01-01")
        denominator = nawi(f"{last_increase_determination_year - 1}-01-01")
        proposed_cap = round_social_security_payroll_cap(
            current_cap * numerator / denominator
        )
        new_cap = max(current_cap, proposed_cap)
        cap.update(period=f"year:{year}-01-01:1", value=new_cap)
        if new_cap > current_cap:
            last_increase_determination_year = determination_year

    final_value = cap(f"{end_year}-01-01")
    cap.update(start=instant(f"{end_year}-01-01"), value=final_value)


def extend_social_security_wage_indexed_parameters(
    parameters: ParameterNode,
    end_year: int,
) -> None:
    """Extend SSA wage-indexed benefit parameters with statutory lag and rounding."""
    ssa = parameters.gov.ssa
    social_security = ssa.social_security
    nawi = ssa.nawi

    wage_base = social_security.wage_base
    payroll_cap = parameters.gov.irs.payroll.social_security.cap
    qc_threshold = social_security.quarters_of_coverage_threshold
    earnings_test = social_security.earnings_test
    pia = social_security.pia.formula_factors
    sga = ssa.sga

    for year in range(2027, end_year + 1):
        period = f"year:{year}-01-01:1"
        determination_nawi = nawi(f"{year - 2}-01-01")

        wage_base.update(
            period=period,
            value=payroll_cap(f"{year}-01-01"),
        )

        qc_threshold.update(
            period=period,
            value=max(
                qc_threshold(f"{year - 1}-01-01"),
                round_social_security_amount(
                    250 * determination_nawi / nawi("1976-01-01"),
                    10,
                ),
            ),
        )

        earnings_test.exempt_amount_under_fra.update(
            period=period,
            value=max(
                earnings_test.exempt_amount_under_fra(f"{year - 1}-01-01"),
                MONTHS_IN_YEAR
                * round_social_security_amount(
                    670 * determination_nawi / nawi("1992-01-01"),
                    10,
                ),
            ),
        )
        earnings_test.exempt_amount_year_of_fra.update(
            period=period,
            value=max(
                earnings_test.exempt_amount_year_of_fra(f"{year - 1}-01-01"),
                MONTHS_IN_YEAR
                * round_social_security_amount(
                    2_500 * determination_nawi / nawi("2000-01-01"),
                    10,
                ),
            ),
        )

        pia.brackets[1].threshold.update(
            period=period,
            value=round_social_security_amount(
                180 * determination_nawi / nawi("1977-01-01"),
                1,
            ),
        )
        pia.brackets[2].threshold.update(
            period=period,
            value=round_social_security_amount(
                1_085 * determination_nawi / nawi("1977-01-01"),
                1,
            ),
        )

        sga.non_blind.update(
            period=period,
            value=max(
                sga.non_blind(f"{year - 1}-01-01"),
                round_social_security_amount(
                    700 * determination_nawi / nawi("1998-01-01"),
                    10,
                ),
            ),
        )
        sga.blind.update(
            period=period,
            value=max(
                sga.blind(f"{year - 1}-01-01"),
                round_social_security_amount(
                    930 * determination_nawi / nawi("1992-01-01"),
                    10,
                ),
            ),
        )

    for parameter in (
        wage_base,
        qc_threshold,
        earnings_test.exempt_amount_under_fra,
        earnings_test.exempt_amount_year_of_fra,
        pia.brackets[1].threshold,
        pia.brackets[2].threshold,
        sga.non_blind,
        sga.blind,
    ):
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )


def set_all_uprating_parameters(parameters: ParameterNode) -> ParameterNode:
    """
    Extend all uprating parameters through 2100.

    This function programmatically extends various uprating factors used
    throughout the US tax and benefit system, including:
    - IRS uprating (based on Chained CPI-U)
    - SNAP uprating (October values)
    - SSA uprating (January values)
    - HHS poverty guideline uprating (January values)
    """
    END_YEAR = 2100

    # IRS uprating - special case that computes from CPI
    IRS_UPRATING_START_YEAR = 2010
    IRS_LAST_PROJECTED_YEAR = 2035

    uprating_index = parameters.gov.irs.uprating

    # Calculate the growth rate from the last two years of CPI projections
    cpi_second_to_last = get_irs_cpi(parameters, IRS_LAST_PROJECTED_YEAR - 2)
    cpi_last = get_irs_cpi(parameters, IRS_LAST_PROJECTED_YEAR - 1)
    growth_rate = cpi_last / cpi_second_to_last

    # Apply IRS uprating
    for year in range(IRS_UPRATING_START_YEAR, END_YEAR + 1):
        if year <= IRS_LAST_PROJECTED_YEAR:
            # Use actual CPI values through the last projected year
            irs_cpi = get_irs_cpi(parameters, year - 1)
        else:
            # For all years after LAST_PROJECTED_YEAR, apply the constant growth rate
            irs_cpi = uprating_index(f"{year - 1}-01-01") * growth_rate
        uprating_index.update(period=f"year:{year}-01-01:1", value=irs_cpi)
    uprating_index.update(start=instant(f"{END_YEAR}-01-01"), value=irs_cpi)

    # SNAP uprating (October values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.usda.snap.uprating,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=10,
        period_day=1,
    )

    # SSA uprating (January values, last projection year 2035)
    extend_parameter_values(
        parameters.gov.ssa.uprating,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Social Security National Average Wage Index (January values, last
    # projection year 2035). The payroll tax contribution and benefit base is
    # indexed to NAWI, so this must remain available through the full long-run
    # projection horizon.
    extend_parameter_values(
        parameters.gov.ssa.nawi,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Social Security payroll tax cap / contribution and benefit base is
    # derived from NAWI under statute and should not be extrapolated
    # independently.
    extend_social_security_payroll_cap(
        parameters,
        last_projected_year=2035,
        end_year=END_YEAR,
    )

    extend_social_security_wage_indexed_parameters(
        parameters,
        end_year=END_YEAR,
    )

    # HHS poverty guideline uprating (January values, last projection year 2035)
    extend_parameter_values(
        parameters.gov.hhs.uprating,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # CPI-U (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_u,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # Chained CPI-U (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.c_cpi_u,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # CPI-W (February values, last projection year 2034)
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_w,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # ACA benchmark premium uprating (January values, last projection year 2025)
    extend_parameter_values(
        parameters.gov.aca.benchmark_premium_uprating,
        last_projected_year=2025,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # CMS per-capita out-of-pocket medical spending (January values, last
    # projection year 2035). Health expense inputs use this as their uprater.
    extend_parameter_values(
        parameters.calibration.gov.hhs.cms.moop_per_capita,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Gross Social Security benefit inputs should age with gross Social
    # Security benefits, not taxable Social Security income.
    extend_parameter_values(
        parameters.calibration.gov.cbo.social_security,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # CBO income-by-source aggregates are used directly and as anchors for
    # SOI-based income upraters. Extending them in the baseline path keeps
    # long-run nominal data aging independent of scenario-specific reforms.
    for parameter_name in LONG_RUN_CBO_INCOME_BY_SOURCE_PARAMETERS:
        extend_parameter_values(
            getattr(parameters.calibration.gov.cbo.income_by_source, parameter_name),
            last_projected_year=2036,
            end_year=END_YEAR,
            period_month=1,
            period_day=1,
        )

    return parameters
