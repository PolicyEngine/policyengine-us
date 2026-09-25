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


def get_average_for_12_months_ending_august(
    cpi: Parameter,
    year: int,
    projection: Parameter,
) -> float:
    """Average a monthly price index over the 12 months ending August 31.

    Covers September of ``year - 1`` through August of ``year``: the
    calendar-year index under both 26 U.S.C. 1(f)(4) and (6)(B) and
    ORS 315.273(5).

    The BLS index series hold monthly observations through the latest BLS
    release, then CBO's calendar-year averages at February instants; a
    monthly refresh that reaches a February replaces that instant's
    projection with the observed value. Windows with observed months average
    them, carrying the last observation flat through any unobserved tail.
    Windows with no observed month read ``projection``, CBO's projection of
    this 12-month average keyed by the tax year it indexes (``year + 1``);
    a calendar-year average would run about four months of inflation high.
    """
    # February instants can hold annual projections, so only non-February
    # instants identify the end of the observed monthly series (one month
    # conservative when observations end exactly on a February).
    last_observation = max(
        instant(value.instant_str)
        for value in cpi.values_list
        if not value.instant_str.endswith("-02-01")
    )
    window_start = instant(f"{year - 1}-09-01")
    window_months = [
        window_start.offset(month, MONTH) for month in range(MONTHS_IN_YEAR)
    ]
    observed = [month for month in window_months if month <= last_observation]
    if not observed:
        return projection(f"{year + 1}-01-01")
    unobserved_tail = MONTHS_IN_YEAR - len(observed)
    return (
        sum(cpi(month) for month in observed) + cpi(observed[-1]) * unobserved_tail
    ) / MONTHS_IN_YEAR


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    """The C-CPI-U for a calendar year under 26 U.S.C. 1(f)(6)(B).

    The average over the 12 months ending August 31 of ``year``, which
    indexes tax parameters for ``year + 1``.
    """
    cpi = parameters.gov.bls.cpi
    return get_average_for_12_months_ending_august(
        cpi.c_cpi_u, year, cpi.tax_year_projection.c_cpi_u
    )


def get_or_ctc_cola(parameters: ParameterNode, tax_year: int) -> float:
    """Calculate the Oregon Kids' Credit cost-of-living adjustment.

    ORS 315.273(5)(b)-(c): the percentage (if any) by which the monthly
    averaged unchained U.S. City Average CPI-U for the 12 consecutive months
    ending August 31 of the prior calendar year exceeds the monthly averaged
    index for the second quarter of calendar year 2022.
    """
    cpi = parameters.gov.bls.cpi
    base = sum(cpi.cpi_u(f"2022-{month:02d}-01") for month in (4, 5, 6)) / 3
    window = get_average_for_12_months_ending_august(
        cpi.cpi_u, tax_year - 1, cpi.tax_year_projection.cpi_u
    )
    return max(window / base - 1, 0)


def get_irs_cola_denominator(parameters: ParameterNode, base_year: int) -> float:
    """Denominator of the 26 U.S.C. 1(f)(3) cost-of-living adjustment.

    For a provision that substitutes a base year no later than 2016 for
    "calendar year 2016" in 1(f)(3)(A)(ii): the (unchained) CPI for the base
    year multiplied by the 1(f)(3)(B) amount, the C-CPI-U for calendar year
    2016 divided by the CPI for calendar year 2016. The unchained CPI-U
    carries pre-2017 base years onto the chained index.
    """
    if base_year > 2016:
        raise ValueError(
            "1(f)(3)(C) replaces this denominator with the C-CPI-U for base "
            f"years after 2016; got {base_year}."
        )
    cpi = parameters.gov.bls.cpi
    cpi_2016, cpi_base_year = (
        get_average_for_12_months_ending_august(
            cpi.cpi_u, year, cpi.tax_year_projection.cpi_u
        )
        for year in (2016, base_year)
    )
    return cpi_base_year * get_irs_cpi(parameters, 2016) / cpi_2016


def get_irs_cola(
    parameters: ParameterNode,
    tax_year: int,
    base_year: int,
) -> float:
    """Calculate a 26 U.S.C. 1(f)(3) cost-of-living adjustment.

    The percentage (if any) by which the C-CPI-U for the calendar year
    preceding ``tax_year`` exceeds the denominator for ``base_year``; see
    ``get_irs_cola_denominator``.
    """
    chained = get_irs_cpi(parameters, tax_year - 1)
    return max(chained / get_irs_cola_denominator(parameters, base_year) - 1, 0)


# 26 U.S.C. 63(c)(5) limits on a dependent's basic standard deduction:
# parameter name, statutory dollar amount, and 63(c)(4)(B) base year.
DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES = (
    ("amount", 500, 1987),  # 63(c)(5)(A)
    ("additional_earned_income", 250, 1997),  # 63(c)(5)(B)
)


def extend_dependent_standard_deduction_parameters(
    parameters: ParameterNode,
    end_year: int,
) -> None:
    """Project the limits on a dependent's basic standard deduction.

    26 U.S.C. 63(c)(4) increases the 63(c)(5)(A) floor ($500) and the
    63(c)(5)(B) earned income addition ($250) by the 1(f)(3) cost-of-living
    adjustment, substituting calendar year 1987 and 1997 respectively for
    2016, and 1(f)(7)(A) rounds each increase down to the next lowest
    multiple of $50. Each year is computed from the statutory base rather
    than chained from the last rounded value, which can lag the statute by
    a full $50 step; IRS values encoded in the YAML take precedence for
    their own years.
    """
    ROUNDING_INTERVAL = 50
    dependent = parameters.gov.irs.deductions.standard.dependent
    for name, base, base_year in DEPENDENT_STANDARD_DEDUCTION_STATUTORY_BASES:
        parameter = getattr(dependent, name)
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            cola = get_irs_cola(parameters, year, base_year)
            increase = math.floor(base * cola / ROUNDING_INTERVAL) * ROUNDING_INTERVAL
            parameter.update(
                period=f"year:{year}-01-01:1", value=float(base + increase)
            )
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )


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


def extend_wa_millionaires_standard_deduction(
    parameters: ParameterNode,
    end_year: int,
) -> None:
    """Project Washington's millionaires tax standard deduction.

    ESSB 6346, section 316, adjusts the deduction each odd-numbered October,
    beginning in 2029, using the latest CPI-W available on October 1 and its
    value 12 months earlier. The result is rounded to the nearest $1,000,
    cannot decrease, and applies in the following tax year.
    """
    ROUNDING_INTERVAL = 1_000
    deduction = parameters.gov.states.wa.tax.income.millionaires_tax.deductions.standard
    cpi_w = parameters.gov.bls.cpi.cpi_w
    current_amount = deduction("2028-01-01")

    for adjustment_year in range(2029, end_year, 2):
        determination_date = instant(f"{adjustment_year}-10-01")
        latest_cpi_instant = max(
            instant(value.instant_str)
            for value in cpi_w.values_list
            if instant(value.instant_str) <= determination_date
        )
        prior_cpi_instant = latest_cpi_instant.offset(-1, YEAR)
        inflation_factor = cpi_w(latest_cpi_instant) / cpi_w(prior_cpi_instant)
        proposed_amount = (
            round(current_amount * inflation_factor / ROUNDING_INTERVAL)
            * ROUNDING_INTERVAL
        )
        current_amount = max(current_amount, proposed_amount)
        effective_year = adjustment_year + 1
        deduction.update(
            start=instant(f"{effective_year}-01-01"),
            value=float(current_amount),
        )

    deduction.update(
        start=instant(f"{end_year}-01-01"),
        value=deduction(f"{end_year}-01-01"),
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

    # CBO's tax-year CPI projections (January values, last projection year
    # 2036) cover 12-month windows with no BLS observation. Extend them first
    # so every IRS uprating year below has a window average.
    for projection in (
        parameters.gov.bls.cpi.tax_year_projection.c_cpi_u,
        parameters.gov.bls.cpi.tax_year_projection.cpi_u,
    ):
        extend_parameter_values(
            projection,
            last_projected_year=2036,
            end_year=END_YEAR,
            period_month=1,
            period_day=1,
        )

    # IRS uprating: the 26 U.S.C. 1(f)(6)(B) C-CPI-U for the calendar year
    # before each tax year.
    IRS_UPRATING_START_YEAR = 2010
    uprating_index = parameters.gov.irs.uprating
    for year in range(IRS_UPRATING_START_YEAR, END_YEAR + 1):
        irs_cpi = get_irs_cpi(parameters, year - 1)
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

    # Washington's millionaires tax deduction uses an odd-year October
    # adjustment schedule. Must run after the CPI-W extension above so the
    # determination dates are available through the projection horizon.
    extend_wa_millionaires_standard_deduction(parameters, end_year=END_YEAR)

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

    # Unemployment compensation inputs age with CBO's unemployment
    # compensation outlays, which anchor the SOI series past its last total.
    extend_parameter_values(
        parameters.calibration.gov.cbo.unemployment_compensation,
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
    # from the statutory base amounts. Must run after the tax-year CPI
    # projection extension above so projected windows are available.
    extend_or_ctc_parameters(parameters, end_year=END_YEAR)

    # The limits on a dependent's standard deduction follow 26 U.S.C.
    # 63(c)(4)'s chained CPI-U schedule, computed from the statutory 1987 and
    # 1997 bases. Must run after the tax-year CPI projection extension above
    # so projected windows are available.
    extend_dependent_standard_deduction_parameters(parameters, end_year=END_YEAR)

    return parameters
