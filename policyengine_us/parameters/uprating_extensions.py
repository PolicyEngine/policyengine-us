"""Unified script to extend all uprating factors through 2100."""

import math
from typing import Optional, Tuple

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


def get_or_ctc_cola(parameters: ParameterNode, tax_year: int) -> float:
    """Calculate the Oregon Kids' Credit cost-of-living adjustment.

    ORS 315.273(5)(b)-(c): the percentage (if any) by which the monthly
    averaged unchained U.S. City Average CPI-U for the 12 consecutive months
    ending August 31 of the prior calendar year exceeds the monthly averaged
    index for the second quarter of calendar year 2022.

    The CPI-U series holds monthly observations through the latest BLS
    release, then annual projection points at February instants; a monthly
    refresh that reaches a February replaces that instant's projection with
    the observed value. Windows with observed months average them, carrying
    the last observation flat through any unobserved tail; windows with no
    observed month read the tax year's annual projection point, whose
    February instant necessarily lies beyond the last observation and so
    can only hold a projection. No branch reads an instant a refresh could
    have turned from projection into observation.
    """
    cpi = parameters.gov.bls.cpi.cpi_u
    base = sum(cpi(f"2022-{month:02d}-01") for month in (4, 5, 6)) / 3
    # February instants can hold annual projections, so only non-February
    # instants identify the end of the observed monthly series (one month
    # conservative when observations end exactly on a February).
    last_observation = max(
        instant(value.instant_str)
        for value in cpi.values_list
        if not value.instant_str.endswith("-02-01")
    )
    window_start = instant(f"{tax_year - 2}-09-01")
    window_months = [
        window_start.offset(month, MONTH) for month in range(MONTHS_IN_YEAR)
    ]
    observed = [month for month in window_months if month <= last_observation]
    if not observed:
        window = cpi(f"{tax_year - 1}-02-01")
    else:
        unobserved_tail = MONTHS_IN_YEAR - len(observed)
        window = (
            sum(cpi(month) for month in observed) + cpi(observed[-1]) * unobserved_tail
        ) / MONTHS_IN_YEAR
    return max(window / base - 1, 0)


def extend_or_ctc_parameters(parameters: ParameterNode, end_year: int) -> None:
    """Project the Oregon Kids' Credit amount and phase-out start.

    ORS 315.273(5) recomputes both dollar amounts each tax year from the
    statutory bases ($1,000 per child and a $25,000 income threshold),
    applying the cost-of-living adjustment and rounding any increase down to
    the next lower multiple of $50 (subsection (5)(d)). Each year is computed
    from the bases rather than chained from later rounded values, so no
    rounding residue compounds; Department of Revenue published values
    encoded in the YAML take precedence for their own years.
    """
    ROUNDING_INTERVAL = 50
    ctc = parameters.gov.states.children["or"].tax.income.credits.ctc
    for parameter, base in (
        (ctc.amount, 1_000),
        (ctc.reduction.start, 25_000),
    ):
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            cola = get_or_ctc_cola(parameters, year)
            increase = math.floor(base * cola / ROUNDING_INTERVAL) * ROUNDING_INTERVAL
            parameter.update(
                period=f"year:{year}-01-01:1", value=float(base + increase)
            )
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )


def extend_parameter_values(
    parameter: Parameter,
    last_projected_year: int,
    end_year: int,
    period_month: int = 1,
    period_day: int = 1,
    growth_years: Optional[Tuple[int, int]] = None,
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
        growth_years: Optional (earlier, later) pair to measure the growth
            rate between, instead of the last two projected years — used
            when the final actual embeds a one-off level shift that should
            not compound in the long-run extension.
    """
    # Calculate the growth rate from the last two years of projections
    date_format = f"-{period_month:02d}-{period_day:02d}"
    if growth_years is None:
        growth_years = (last_projected_year - 1, last_projected_year)
    earlier_year, later_year = growth_years
    second_to_last_value = parameter(f"{earlier_year}{date_format}")
    last_value = parameter(f"{later_year}{date_format}")
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

    # ACA benchmark premium uprating (January values, last actual 2026).
    # The published 2026 actual is 25.8% above 2025; keep long-run growth
    # at the 2024-2025 trend so the one-off jump does not compound.
    extend_parameter_values(
        parameters.gov.aca.benchmark_premium_uprating,
        last_projected_year=2026,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        growth_years=(2024, 2025),
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

    # Oregon Kids' Credit dollar amounts follow the ORS 315.273(5)
    # cost-of-living schedule (unchained CPI-U over a 2022 Q2 base), computed
    # from the statutory base amounts. Must run after the CPI-U extension
    # above so projected windows are available.
    extend_or_ctc_parameters(parameters, end_year=END_YEAR)

    return parameters
