"""Unified script to extend all uprating factors through 2100."""

import math
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, Optional, Tuple

from policyengine_us.model_api import *
from policyengine_core.periods import Instant, instant


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

# Long-range annual growth rates from the 2026 Medicare Trustees Report
# (transmitted 2026-06-09, sha256
# ffa56b9137006872300b0346149eae1613d09a172b6ba118aad48e66dfc48fa8), as
# {year: rate} knots for extend_parameter_values(long_range_growth=...). The
# Trustees set the growth rates for years 11 through 25 of their projection
# (2036-2050) by interpolating between the rate at the end of the short-range
# period and the rate at the start of the last 50 years (file pages 24 and
# 180), and the long-range rates then decline gradually from 2050 to 2100
# (file pages 23 and 173). They publish only the 2050 and 2100 rates, so the
# path between those two knots is linear here. That is an approximation: the
# Trustees' own path is not a straight line, as their income-technology
# elasticity declines at a slowing pace and their price elasticity follows a
# non-linear path between 2050 and 2100 (file page 175).
#
# Per capita overall health spending grows at GDP plus 0.7 percent (4.3
# percent) in 2050, declining gradually to GDP plus 0.4 percent (4.1 percent)
# by 2100 (file page 173). The Trustees publish no long-range rate for
# out-of-pocket spending or private insurance (Table V.B5, file page 200,
# stops private health insurance in 2035), so this rate serves those series:
# the factors model behind it holds insurance coverage unchanged (file page
# 175), and the Trustees see only a small likelihood that one part of the
# health sector grows indefinitely at significantly faster rates than the
# others (file page 177). The Trustees extend CMS's national health
# expenditure projections past 2033 by the same long-range methods (Table
# V.B5, note 1, file page 200).
HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH = {2050: 0.043, 2100: 0.041}

# The Trustees' Medicare cost growth rates exclude the effects of the aging of
# the population and of changes in the sex and time-to-death mix of
# enrollees (file page 172, footnote 81). Spending per enrollee includes
# them: Table II.D1 (file page 29) puts the beneficiary demographic mix at
# -0.1 percent a year in 2051-2100 for each of Parts A, B and D.
MEDICARE_LONG_RANGE_DEMOGRAPHIC_MIX = -0.001


def with_medicare_demographic_mix(cost_growth: Dict[int, float]) -> Dict[int, float]:
    """Medicare spending per enrollee growth: the Trustees' cost growth rate
    (excluding demographic impacts) compounded with the long-range
    demographic mix."""
    return {
        year: (1 + rate) * (1 + MEDICARE_LONG_RANGE_DEMOGRAPHIC_MIX) - 1
        for year, rate in cost_growth.items()
    }


# Parts A, B and D combined: 3.8 percent in 2050, declining to 3.7 percent by
# 2100 (file pages 23 and 180).
MEDICARE_PER_ENROLLEE_LONG_RANGE_GROWTH = with_medicare_demographic_mix(
    {2050: 0.038, 2100: 0.037}
)
# Part B: 3.8 percent in 2050, remaining at 3.8 percent by 2100 (file pages 23
# and 180).
MEDICARE_PART_B_PER_ENROLLEE_LONG_RANGE_GROWTH = with_medicare_demographic_mix(
    {2050: 0.038, 2100: 0.038}
)
# Part D: 4.1 percent in 2050, declining to 3.9 percent by 2100 (file pages 23
# and 179).
MEDICARE_PART_D_PER_ENROLLEE_LONG_RANGE_GROWTH = with_medicare_demographic_mix(
    {2050: 0.041, 2100: 0.039}
)


def get_irs_cpi(parameters: ParameterNode, year: int) -> float:
    """Average chained CPI-U from August of ``year - 1`` through July of ``year``.

    26 U.S.C. 1(f) uses the 12 months ending August; #9105 tracks the
    one-month offset.
    """
    cpi = parameters.gov.bls.cpi.c_cpi_u
    end = instant(f"{year}-08-01")
    start = end.offset(-MONTHS_IN_YEAR, MONTH)
    monthly_cpi_values = []
    for month in range(MONTHS_IN_YEAR):
        monthly_cpi_values += [cpi(start.offset(month, MONTH))]
    return sum(monthly_cpi_values) / MONTHS_IN_YEAR


def get_average_for_12_months_ending_august(cpi: Parameter, year: int) -> float:
    """Average a monthly price index over the 12 months ending August 31.

    Covers September of ``year - 1`` through August of ``year``: the
    calendar-year index under both 26 U.S.C. 1(f)(4) and (6)(B) and
    ORS 315.273(5).

    The BLS index series hold monthly observations through the latest BLS
    release, then annual projection points at February instants; a monthly
    refresh that reaches a February replaces that instant's projection with
    the observed value. Windows with observed months average them, carrying
    the last observation flat through any unobserved tail; windows with no
    observed month read the year's annual projection point, whose
    February instant necessarily lies beyond the last observation and so
    can only hold a projection. No branch reads an instant a refresh could
    have turned from projection into observation.
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
        # Since #7394 the projection points cite CBO's calendar-year
        # averages, which run about 0.7% above the 12-months-ending-August
        # averages this window stands for, so projected windows read slightly
        # high until that series is fixed (#9608).
        return cpi(f"{year}-02-01")
    unobserved_tail = MONTHS_IN_YEAR - len(observed)
    return (
        sum(cpi(month) for month in observed) + cpi(observed[-1]) * unobserved_tail
    ) / MONTHS_IN_YEAR


def get_cpi_u_average_for_12_months_ending_august(
    parameters: ParameterNode, year: int
) -> float:
    """Average the CPI-U series over the 12 months ending August 31."""
    return get_average_for_12_months_ending_august(parameters.gov.bls.cpi.cpi_u, year)


def get_or_ctc_cola(parameters: ParameterNode, tax_year: int) -> float:
    """Calculate the Oregon Kids' Credit cost-of-living adjustment.

    ORS 315.273(5)(b)-(c): the percentage (if any) by which the monthly
    averaged unchained U.S. City Average CPI-U for the 12 consecutive months
    ending August 31 of the prior calendar year exceeds the monthly averaged
    index for the second quarter of calendar year 2022.
    """
    cpi = parameters.gov.bls.cpi.cpi_u
    base = sum(cpi(f"2022-{month:02d}-01") for month in (4, 5, 6)) / 3
    window = get_average_for_12_months_ending_august(cpi, tax_year - 1)
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
    cpi = parameters.gov.bls.cpi.cpi_u
    chained_2016 = get_average_for_12_months_ending_august(
        parameters.gov.bls.cpi.c_cpi_u, 2016
    )
    cpi_2016 = get_average_for_12_months_ending_august(cpi, 2016)
    cpi_base_year = get_average_for_12_months_ending_august(cpi, base_year)
    return cpi_base_year * chained_2016 / cpi_2016


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
    chained = get_average_for_12_months_ending_august(
        parameters.gov.bls.cpi.c_cpi_u, tax_year - 1
    )
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
    a full $50 step; IRS and CBO values encoded in the YAML take precedence
    for their own years.
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


# 26 U.S.C. 62(d)(3) indexing of the 62(a)(2)(D) educator expense cap:
# statutory dollar amount and 1(f)(3) base year.
EDUCATOR_EXPENSE_CAP_STATUTORY_BASE = (250, 2014)


def extend_educator_expense_cap(parameters: ParameterNode, end_year: int) -> None:
    """Project the per-educator cap on the educator expense deduction.

    26 U.S.C. 62(d)(3) increases the $250 amount in 62(a)(2)(D) by the
    1(f)(3) cost-of-living adjustment, substituting calendar year 2014 for
    2016, and rounds the increase to the nearest multiple of $50. Each year
    is computed from the statutory base rather than chained from the last
    rounded value, which can put a $50 step a year or more early or late;
    IRS values encoded in the YAML take precedence for their own years.
    """
    ROUNDING_INTERVAL = 50
    base, base_year = EDUCATOR_EXPENSE_CAP_STATUTORY_BASE
    cap = parameters.gov.irs.ald.educator_expense.cap
    first_projected_year = 1 + max(
        int(value.instant_str[:4]) for value in cap.values_list
    )
    for year in range(first_projected_year, end_year + 1):
        cola = get_irs_cola(parameters, year, base_year)
        # Nearest multiple of $50; an exact half rounds up.
        increase = math.floor(base * cola / ROUNDING_INTERVAL + 0.5) * ROUNDING_INTERVAL
        cap.update(period=f"year:{year}-01-01:1", value=float(base + increase))
    cap.update(
        start=instant(f"{end_year}-01-01"),
        value=cap(f"{end_year}-01-01"),
    )


def get_average_for_12_months_ending_march(cpi: Parameter, year: int) -> float:
    """Average a monthly price index over the 12 months ending March 31.

    Covers April of ``year - 1`` through March of ``year``: the calendar-year
    index for the HSA amounts, which 26 U.S.C. 223(g)(1) obtains by applying
    1(f)(4) "by substituting 'March 31' for 'August 31'". Observed months
    are read as published; unobserved months are interpolated toward the
    index's calendar-year projection points by
    ``get_projected_cpi_u_for_month``, so a window that straddles the last
    observation is neither held flat nor read from a point centred months
    away from it.
    """
    end = instant(f"{year}-03-01")
    return (
        sum(
            get_projected_cpi_u_for_month(cpi, end.offset(-month, MONTH))
            for month in range(MONTHS_IN_YEAR)
        )
        / MONTHS_IN_YEAR
    )


# 26 U.S.C. 223(b)(2) dollar amounts by coverage (parameter name, amount) and
# the base year 223(g)(1)(B)(i) substitutes for calendar year 2016.
HSA_CONTRIBUTION_LIMIT_STATUTORY_BASES = (
    ("self_only", 2_250),  # 223(b)(2)(A)
    ("family", 4_500),  # 223(b)(2)(B)
)
HSA_CONTRIBUTION_LIMIT_BASE_YEAR = 1997


def get_hsa_cola_denominator(parameters: ParameterNode) -> float:
    """Denominator of the 26 U.S.C. 223(g)(1) cost-of-living adjustment.

    The CPI for 1997, the base year 223(g)(1)(B)(i) substitutes for calendar
    year 2016, averaged over the 12 months ending March 31 as 223(g)(1)
    applies 1(f)(4), times the 1(f)(3)(B) ratio of the C-CPI-U to the CPI for
    calendar year 2016. That ratio keeps its 12 months ending August 31, as
    for every other 1(f)(3) amount; see ``get_hsa_cola``.
    """
    cpi = parameters.gov.bls.cpi
    ratio_2016 = get_average_for_12_months_ending_august(
        cpi.c_cpi_u, 2016
    ) / get_average_for_12_months_ending_august(cpi.cpi_u, 2016)
    return (
        get_average_for_12_months_ending_march(
            cpi.cpi_u, HSA_CONTRIBUTION_LIMIT_BASE_YEAR
        )
        * ratio_2016
    )


def get_hsa_cola(
    parameters: ParameterNode,
    tax_year: int,
    denominator: Optional[float] = None,
) -> float:
    """The 26 U.S.C. 223(g)(1) cost-of-living adjustment for ``tax_year``.

    The 1(f)(3) adjustment with calendar year 1997 in place of 2016, and with
    1(f)(4) applied by substituting March 31 for August 31: the percentage
    (if any) by which the C-CPI-U for the calendar year before ``tax_year``,
    averaged over the 12 months ending March 31, exceeds
    ``get_hsa_cola_denominator``. These windows reproduce every self-only and
    family limit the IRS published for 2019 through 2027, and Rev. Proc.
    2018-18's limits for 2018, from the BLS series in ``gov.bls.cpi``
    (``tests/core/test_hsa_contribution_limits.py``). Taking the 2016 ratio
    over the 12 months ending March 31 as well misses 3 of the 18 values for
    2019 to 2027. ``denominator`` lets a caller computing many years pass it
    once.
    """
    if denominator is None:
        denominator = get_hsa_cola_denominator(parameters)
    chained = get_average_for_12_months_ending_march(
        parameters.gov.bls.cpi.c_cpi_u, tax_year - 1
    )
    return max(chained / denominator - 1, 0)


def extend_hsa_contribution_limits(parameters: ParameterNode, end_year: int) -> None:
    """Project the HSA contribution limits for self-only and family coverage.

    26 U.S.C. 223(g) increases the 223(b)(2) amounts ($2,250 self-only and
    $4,500 family) by the cost-of-living adjustment in ``get_hsa_cola`` and
    rounds each increase to the nearest multiple of $50. Each year is
    computed from the statutory base rather than chained from the last
    rounded value; IRS values encoded in the YAML take precedence for their
    own years.
    """
    ROUNDING_INTERVAL = 50
    limit = parameters.gov.irs.gross_income.health_savings_account_contributions.limit
    denominator = get_hsa_cola_denominator(parameters)
    colas = {}
    for name, base in HSA_CONTRIBUTION_LIMIT_STATUTORY_BASES:
        parameter = getattr(limit, name)
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            if year not in colas:
                colas[year] = get_hsa_cola(parameters, year, denominator)
            # Nearest multiple of $50; an exact half rounds up.
            increase = (
                math.floor(base * colas[year] / ROUNDING_INTERVAL + 0.5)
                * ROUNDING_INTERVAL
            )
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


def get_nyc_income_tax_elimination_credit_cola(
    parameters: ParameterNode, tax_year: int
) -> float:
    """Calculate the NYC income tax elimination credit cost-of-living adjustment.

    Tax Law § 1310(h)(1)(B)(iii): the percentage by which the consumer price
    index for the calendar year preceding the tax year exceeds the consumer
    price index for calendar year 2024. Section 1310(h)(3)(A) defines a
    calendar year's index as the average CPI-U for all urban consumers for
    the 12 months ending August 31 of that year.
    """
    CPI_BASE_YEAR = 2024
    base = get_cpi_u_average_for_12_months_ending_august(parameters, CPI_BASE_YEAR)
    window = get_cpi_u_average_for_12_months_ending_august(parameters, tax_year - 1)
    return max(window / base - 1, 0)


def extend_nyc_income_tax_elimination_credit_thresholds(
    parameters: ParameterNode, end_year: int
) -> None:
    """Project the NYC income tax elimination credit income thresholds.

    Tax Law § 1310(h)(1)(B)(iii) multiplies the statutory amounts, which
    apply to tax year 2025, by one plus the cost-of-living adjustment for
    each tax year from 2026. Each year is computed from the statutory
    amounts rather than chained from the prior year. The statute specifies
    no rounding, so none is applied. Department of Taxation and Finance
    published values encoded in the YAML take precedence for their own
    years.
    """
    STATUTORY_YEAR = 2025
    thresholds = parameters.gov.local.ny.nyc.tax.income.credits.income_tax_elimination.income_threshold
    for scale in thresholds.children.values():
        for bracket in scale.brackets:
            amount = bracket.amount
            base = amount(f"{STATUTORY_YEAR}-01-01")
            first_projected_year = 1 + max(
                int(value.instant_str[:4]) for value in amount.values_list
            )
            for year in range(first_projected_year, end_year + 1):
                cola = get_nyc_income_tax_elimination_credit_cola(parameters, year)
                amount.update(
                    period=f"year:{year}-01-01:1", value=float(base * (1 + cola))
                )
            amount.update(
                start=instant(f"{end_year}-01-01"),
                value=amount(f"{end_year}-01-01"),
            )


def get_projected_cpi_u_for_month(cpi: Parameter, month: Instant) -> float:
    """CPI-U for a month, interpolated toward CBO's projections if unobserved.

    The model's CPI-U series holds BLS monthly observations, then CBO's
    calendar-year averages as projection points at February instants (see
    ``get_average_for_12_months_ending_august`` and #9608; the "# YYYY
    value" comments in cpi_u.yaml label the tax year a point feeds, not its
    calendar year). A calendar-year average sits halfway between June and
    July of its year. So an unobserved month is interpolated geometrically,
    by month, between the last observation and the next projection point
    placed there, or between two such points; past the last point the index
    holds flat.

    As in ``get_average_for_12_months_ending_august``, only non-February
    instants identify the end of the observed series, and no branch reads
    an instant a refresh could have turned from projection into
    observation: a February in the last observation's year is never an
    anchor. That only matters when observations end in January (any later
    month already follows that February): the February may then hold that
    year's projection or an observation, so it is skipped, and the months
    after January interpolate toward the next year's point.
    """
    last_observation = max(
        instant(value.instant_str)
        for value in cpi.values_list
        if not value.instant_str.endswith("-02-01")
    )
    if month <= last_observation:
        return cpi(month)

    def month_index(date: Instant) -> float:
        return 12 * date.year + date.month - 1

    anchors = [(month_index(last_observation), cpi(last_observation))] + sorted(
        (12 * int(value.instant_str[:4]) + 5.5, value.value)
        for value in cpi.values_list
        if value.instant_str.endswith("-02-01")
        and int(value.instant_str[:4]) > last_observation.year
    )
    target = month_index(month)
    for (start, start_level), (end, end_level) in zip(anchors, anchors[1:]):
        if target <= end:
            share = (target - start) / (end - start)
            return start_level * (end_level / start_level) ** share
    return anchors[-1][1]


def get_la_cpi_u_percentage_increase(cpi: ParameterNode, year: int) -> float:
    """The CPI-U percentage increase for calendar ``year``, as BLS reports it.

    La. R.S. 47:294(B) and 47:44.1(A) multiply the prior year's amount by
    "the percentage increase in the Consumer Price Index ... (CPI-U), as
    reported by the United States Department of Labor, Bureau of Labor
    Statistics ... for the previous calendar year". For tax year 2026, LDR
    Revenue Information Bulletin 26-019 applied 2.7%. The bulletin names no
    comparison months, but 2.7% is the December 2024 to December 2025 change
    as BLS reported it (324.054 / 315.605, not seasonally adjusted: 2.677%).
    The 2025 annual-average change (321.943 / 313.689) was 2.6%, and the
    unrounded 2.677% would give $12,835 rather than the bulletin's $12,838.
    So the percentage is the December-over-December change rounded to one
    decimal place, as BLS reports it. A fall in the index is not an
    increase, so the percentage is never negative.

    ``cpi`` is the ``gov.bls.cpi`` node. BLS reports the change from the not
    seasonally adjusted index, so the published Decembers in
    ``cpi_u_nsa_december`` are used when both years have one. Otherwise
    both Decembers come from the model's CPI-U series (seasonally adjusted
    from January 2024), through ``get_projected_cpi_u_for_month``; mixing
    the two would add December's seasonal factor (about 0.6% in 2025) to
    the change.
    """
    december = cpi.cpi_u_nsa_december
    published = {int(value.instant_str[:4]) for value in december.values_list}
    if {year - 1, year} <= published:
        current = december(f"{year}-12-01")
        prior = december(f"{year - 1}-12-01")
    else:
        current = get_projected_cpi_u_for_month(cpi.cpi_u, instant(f"{year}-12-01"))
        prior = get_projected_cpi_u_for_month(cpi.cpi_u, instant(f"{year - 1}-12-01"))
    change = 100 * (Decimal(repr(current)) / Decimal(repr(prior)) - 1)
    percentage = change.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return float(max(percentage, 0))


def adjust_la_amount_for_inflation(prior_amount: float, percentage: float) -> float:
    """Apply a La. R.S. 47:294(B) / 47:44.1(A) adjustment to a prior amount.

    RIB 26-019's amounts are the adjusted amounts rounded to the nearest
    dollar, with half dollars rounding up: $12,500 x 1.027 = $12,837.50
    became $12,838. The arithmetic is decimal because in binary floating
    point 12,500 x 1.027 is just below 12,837.5 and would round down.
    """
    adjusted = Decimal(str(prior_amount)) * (100 + Decimal(str(percentage))) / 100
    return float(adjusted.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def extend_la_cpi_u_indexed_amounts(parameters: ParameterNode, end_year: int) -> None:
    """Project Louisiana's CPI-U-indexed standard deduction and retirement cap.

    Each year after the last LDR-published amount, the single and
    married-separate standard deduction (R.S. 47:294(A)(1)) and the age-65
    retirement income exemption (R.S. 47:44.1(A)) become the prior year's
    amount adjusted by the prior calendar year's CPI-U percentage increase
    (see ``get_la_cpi_u_percentage_increase``), rounded to the nearest
    dollar. The joint, head of household and surviving spouse deduction is
    200% of the single amount (R.S. 47:294(A)(2)), so it doubles the rounded
    single amount rather than being adjusted on its own. Amounts encoded in
    the YAML take precedence for their own years.

    Like the other projections in this module, the values are fixed when
    the parameter tree is built. A reform that changes the single amount
    does not carry through to the other filing statuses or later years.
    """
    la = parameters.gov.states.la.tax.income
    cpi = parameters.gov.bls.cpi
    standard = la.deductions.standard.amount
    retirement_caps = [
        bracket.amount
        for bracket in la.exempt_income.retirement.cap.brackets
        if bracket.threshold(f"{end_year}-01-01") == 65
    ]
    if len(retirement_caps) != 1:
        raise ValueError(
            "Expected one age-65 bracket in the Louisiana retirement income "
            f"exemption cap; found {len(retirement_caps)}."
        )
    percentages = {}
    for parameter in (standard.SINGLE, retirement_caps[0]):
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            if year - 1 not in percentages:
                percentages[year - 1] = get_la_cpi_u_percentage_increase(cpi, year - 1)
            parameter.update(
                period=f"year:{year}-01-01:1",
                value=adjust_la_amount_for_inflation(
                    parameter(f"{year - 1}-01-01"), percentages[year - 1]
                ),
            )
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )
    for parameter, share_of_single in (
        (standard.SEPARATE, 1),
        (standard.JOINT, 2),
        (standard.HEAD_OF_HOUSEHOLD, 2),
        (standard.SURVIVING_SPOUSE, 2),
    ):
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            parameter.update(
                period=f"year:{year}-01-01:1",
                value=share_of_single * standard.SINGLE(f"{year}-01-01"),
            )
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )


def get_cms_cpi_u_percentage_increase(cpi: ParameterNode, year: int) -> float:
    """The CPI-U percentage increase CMS applies to ``year``'s home equity limits.

    42 USC 1396p(f)(1)(C) increases the Medicaid long-term care home equity
    limits "from year to year based on the percentage increase in the consumer
    price index for all urban consumers ... rounded to the nearest $1,000".
    CMS's annual SSI and spousal impoverishment bulletins report a "CPI
    Increase" for each year to one decimal place: 1.7% for 2020, 1.4% for
    2021, 5.4% for 2022, 2.4% for 2025 and 3.0% for 2026. Each is the
    September-to-September change in the not seasonally adjusted CPI-U ending
    the September before the year, rounded to one decimal place. CMS applies
    the rounded percentage: $893,000 x 1.014 = $905,502 became the published
    2021 maximum of $906,000, where the unrounded 1.371% would give $905,000.
    A fall in the index is not an increase, so the percentage is never
    negative.

    ``cpi`` is the ``gov.bls.cpi`` node. The published Septembers in
    ``cpi_u_nsa_september`` are used when both are available. Otherwise both
    Septembers come from the model's CPI-U series (seasonally adjusted from
    January 2024) through ``get_projected_cpi_u_for_month``, so the two are
    never mixed.
    """
    september = cpi.cpi_u_nsa_september
    published = {int(value.instant_str[:4]) for value in september.values_list}
    if {year - 2, year - 1} <= published:
        current = september(f"{year - 1}-09-01")
        prior = september(f"{year - 2}-09-01")
    else:
        current = get_projected_cpi_u_for_month(cpi.cpi_u, instant(f"{year - 1}-09-01"))
        prior = get_projected_cpi_u_for_month(cpi.cpi_u, instant(f"{year - 2}-09-01"))
    change = 100 * (Decimal(repr(current)) / Decimal(repr(prior)) - 1)
    percentage = change.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return float(max(percentage, 0))


def adjust_home_equity_limit_for_inflation(
    prior_amount: float, percentage: float
) -> float:
    """Apply a 42 USC 1396p(f)(1)(C) increase, rounded to the nearest $1,000."""
    adjusted = Decimal(str(prior_amount)) * (100 + Decimal(str(percentage))) / 100
    thousands = (adjusted / 1_000).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return float(thousands * 1_000)


# P.L. 119-21 section 71108(c): the $1,000,000 cap on non-agricultural homes
# applies beginning January 1, 2028.
HOME_EQUITY_NON_AGRICULTURAL_CAP_START_YEAR = 2028


def extend_medicaid_home_equity_limits(
    parameters: ParameterNode, end_year: int
) -> None:
    """Project the CPI-indexed Medicaid long-term care home equity limits.

    Each year after their last CMS-published values, the minimum and
    agricultural home equity limits become their prior year's limit increased
    by that year's CPI-U percentage (see ``get_cms_cpi_u_percentage_increase``), rounded to
    the nearest $1,000, effective January 1. Before P.L. 119-21 section 71108
    caps other homes at $1,000,000 beginning in 2028, the agricultural and
    non-agricultural limits are the same indexed maximum, so each year before
    the cap with no non-agricultural value in the YAML takes the agricultural
    projection. Amounts encoded in the YAML take precedence for their own
    years.

    Like the other projections in this module, the values are fixed when the
    parameter tree is built.
    """
    home_equity = parameters.gov.hhs.medicaid.eligibility.long_term_care.home_equity
    cpi = parameters.gov.bls.cpi
    agricultural = home_equity.agricultural_limit
    percentages = {}
    for parameter in (home_equity.minimum_limit, agricultural):
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            if year not in percentages:
                percentages[year] = get_cms_cpi_u_percentage_increase(cpi, year)
            parameter.update(
                period=f"year:{year}-01-01:1",
                value=adjust_home_equity_limit_for_inflation(
                    parameter(f"{year - 1}-01-01"), percentages[year]
                ),
            )
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )
    non_agricultural = home_equity.limit
    encoded_years = {
        int(value.instant_str[:4]) for value in non_agricultural.values_list
    }
    for year in range(
        min(encoded_years) + 1, HOME_EQUITY_NON_AGRICULTURAL_CAP_START_YEAR
    ):
        if year not in encoded_years:
            non_agricultural.update(
                period=f"year:{year}-01-01:1",
                value=agricultural(f"{year}-01-01"),
            )


def get_cms_spousal_impoverishment_multiplier(
    parameters: ParameterNode, year: int
) -> float:
    """CMS's cumulative 42 USC 1396r-5(g) CPI-U adjustment multiplier.

    The statutory CSRA and MMMNA bases are adjusted by CPI-U growth from
    September 1988 to September before the eligibility year. CMS's annual
    bulletins round this cumulative percentage to one decimal place before
    applying it: the 2026 increase is 171.1%, giving a multiplier of 2.711.
    This cumulative calculation avoids compounding rounded annual increases.

    Published not-seasonally-adjusted Septembers take precedence. Beyond the
    last publication, the model's projected CPI-U growth is applied to that
    published NSA level. Normalizing the forecast at the last common month
    avoids treating the SA/NSA level difference as future inflation.
    """
    cpi = parameters.gov.bls.cpi
    indexing = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal.indexing
    date = f"{year}-01-01"
    base_year = int(indexing.base_year(date))
    reference_month = int(indexing.reference_month(date))
    rounding_interval = Decimal(str(indexing.percentage_rounding_interval(date)))
    base_date = f"{base_year}-{reference_month:02d}-01"
    current_date = f"{year - 1}-{reference_month:02d}-01"
    september = cpi.cpi_u_nsa_september
    published_dates = {value.instant_str for value in september.values_list}
    base = Decimal(str(september(base_date)))
    if current_date in published_dates:
        current = Decimal(str(september(current_date)))
    else:
        anchor_date = max(date for date in published_dates if date < current_date)
        anchor = Decimal(str(september(anchor_date)))
        projected_current = Decimal(
            str(get_projected_cpi_u_for_month(cpi.cpi_u, instant(current_date)))
        )
        projected_anchor = Decimal(
            str(get_projected_cpi_u_for_month(cpi.cpi_u, instant(anchor_date)))
        )
        current = anchor * projected_current / projected_anchor
    change = 100 * (current / base - 1)
    rounded_change = (change / rounding_interval).quantize(
        Decimal(1), rounding=ROUND_HALF_UP
    ) * rounding_interval
    return float(1 + max(rounded_change, 0) / 100)


def extend_medicaid_spousal_impoverishment_standards(
    parameters: ParameterNode, end_year: int
) -> None:
    """Project federal CSRA bounds and the MMMNA maximum under 1396r-5(g).

    Each unpublished year's standards apply the cumulative CPI-U multiplier
    to the statutory dollar bases, effective January 1. CMS-published values
    encoded in YAML take precedence for their years. July's minimum MMMNA
    follows the separate poverty-guideline schedule and is not changed here.

    Like the other projections in this module, the values are fixed when the
    parameter tree is built; later reforms can override individual years.
    """
    federal = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal
    multipliers = {}
    for parameter, statutory_base in (
        (federal.csra.minimum, federal.csra.minimum_base),
        (federal.csra.maximum, federal.csra.maximum_base),
        (federal.mmmna.maximum, federal.mmmna.maximum_base),
    ):
        first_projected_year = 1 + max(
            int(value.instant_str[:4]) for value in parameter.values_list
        )
        for year in range(first_projected_year, end_year + 1):
            if year not in multipliers:
                multipliers[year] = get_cms_spousal_impoverishment_multiplier(
                    parameters, year
                )
            value = Decimal(str(statutory_base(f"{year}-01-01"))) * Decimal(
                str(multipliers[year])
            )
            parameter.update(period=f"year:{year}-01-01:1", value=float(value))
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


# 42 U.S.C. 1395i-2(d)(4): an individual with 30 to 39 quarters of coverage
# pays the Part A premium reduced by 45 percent.
MEDICARE_PART_A_REDUCED_PREMIUM_SHARE = 0.55


def round_half_up(value: float, interval: float) -> float:
    """Round ``value`` to the nearest multiple of ``interval``, sending an
    amount midway between two multiples to the higher one, as 42 U.S.C.
    1395i-2(d)(2) does for the Part A premium and 1395e(b)(1) for the Part A
    deductible."""
    step = Decimal(repr(interval))
    return float(
        (Decimal(repr(value)) / step).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        * step
    )


def extend_medicare_part_a_premiums(parameters: ParameterNode, end_year: int) -> None:
    """Project the Medicare Part A full and reduced monthly premiums.

    Each year after the last CMS-published one, the full premium is the last
    published premium grown with the Medicare Trustees' projected standard
    premium, rounded to the nearest dollar with 50-cent amounts rounded up
    (42 U.S.C. 1395i-2(d)(2)). The reduced premium is the full premium less
    45 percent (1395i-2(d)(4)), rounded the same way; CMS's published
    reduced premiums follow that rule in every year from 2015 to 2026. CMS
    values encoded in the YAML take precedence for their own years.
    """
    part_a = parameters.gov.hhs.medicare.part_a
    series = parameters.calibration.gov.hhs.cms.medicare_part_a_premium_per_enrollee
    full, reduced = part_a.full_premium, part_a.reduced_premium

    def last_published_year(parameter: Parameter) -> int:
        return max(int(value.instant_str[:4]) for value in parameter.values_list)

    last_full_year = last_published_year(full)
    last_reduced_year = last_published_year(reduced)
    base_period = f"{last_full_year}-01-01"
    scale = full(base_period) / series(base_period)
    for year in range(last_full_year + 1, end_year + 1):
        period = f"{year}-01-01"
        full_premium = round_half_up(scale * series(period), 1)
        full.update(period=f"year:{period}:1", value=full_premium)
    for year in range(last_reduced_year + 1, end_year + 1):
        period = f"{year}-01-01"
        reduced.update(
            period=f"year:{period}:1",
            value=round_half_up(
                MEDICARE_PART_A_REDUCED_PREMIUM_SHARE * full(period), 1
            ),
        )
    for parameter in (full, reduced):
        parameter.update(
            start=instant(f"{end_year}-01-01"),
            value=parameter(f"{end_year}-01-01"),
        )


def extend_medicare_part_a_deductible(parameters: ParameterNode, end_year: int) -> None:
    """Project the Medicare Part A inpatient hospital deductible.

    Each year after the last CMS-published one, the deductible is the last
    published deductible grown with the Medicare Trustees' projected
    deductible, rounded to the nearest multiple of $4. An amount midway
    between two multiples goes to the higher one (42 U.S.C. 1395e(b)(1)),
    which core's ``nearest`` uprating rounding would send to the even
    multiple. CMS values encoded in the YAML take precedence for their own
    years.
    """
    deductible = parameters.gov.hhs.medicare.part_a.deductible
    series = parameters.calibration.gov.hhs.cms.medicare_part_a_deductible
    last_year = max(int(value.instant_str[:4]) for value in deductible.values_list)
    base_period = f"{last_year}-01-01"
    scale = deductible(base_period) / series(base_period)
    for year in range(last_year + 1, end_year + 1):
        period = f"{year}-01-01"
        deductible.update(
            period=f"year:{period}:1",
            value=round_half_up(scale * series(period), 4),
        )
    deductible.update(
        start=instant(f"{end_year}-01-01"),
        value=deductible(f"{end_year}-01-01"),
    )


# 42 U.S.C. 1395r(i)(3)(C)(i)(III): the dollar amounts of the applicable
# percentage table for an unmarried individual, before the (5) inflation
# adjustment. The first is also the (2)(A) threshold amount.
MEDICARE_IRMAA_STATUTORY_AMOUNTS = (85_000, 107_000, 133_500, 160_000)
MEDICARE_IRMAA_STATUTORY_TOP_AMOUNT = 500_000
# 1395r(i)(5)(A): for 2020 on, CPI-U for the 12 months ending August of the
# preceding year over the 12 months ending August 2018. (5)(C): the $500,000
# amount is not adjusted before 2028, and from 2028 is adjusted against the 12
# months ending August 2026.
MEDICARE_IRMAA_CPI_BASE_YEAR = 2018
MEDICARE_IRMAA_FIRST_INDEXED_YEAR = 2020
MEDICARE_IRMAA_TOP_CPI_BASE_YEAR = 2026
MEDICARE_IRMAA_TOP_FIRST_INDEXED_YEAR = 2028
# 1395r(i)(3)(C)(i)(III): the applicable percentage of each adjusted tier, by
# bracket of each filing status's scale (the first bracket pays no
# adjustment). A married individual filing separately who lives with the
# spouse pays an adjustment only above the unmarried threshold amount
# ((i)(1)), which is above where (C)(iii) starts the 80 percent tier, so that
# scale has only the 80 and 85 percent tiers.
MEDICARE_IRMAA_APPLICABLE_PERCENTAGES = {
    "single": (0.35, 0.50, 0.65, 0.80, 0.85),
    "joint": (0.35, 0.50, 0.65, 0.80, 0.85),
    "head_of_household": (0.35, 0.50, 0.65, 0.80, 0.85),
    "surviving_spouse": (0.35, 0.50, 0.65, 0.80, 0.85),
    "separate": (0.80, 0.85),
}


def round_medicare_irmaa_amount(amount: float) -> float:
    """Round an adjusted dollar amount to the nearest multiple of $1,000.

    42 U.S.C. 1395r(i)(5)(B) names no rule for an amount midway between two
    multiples; it rounds up here.
    """
    return float(
        (Decimal(repr(amount)) / 1_000).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        * 1_000
    )


def get_medicare_irmaa_unmarried_amounts(
    parameters: ParameterNode, year: int
) -> Tuple[Tuple[float, ...], float]:
    """The unmarried dollar amounts of the IRMAA table for ``year``.

    Returns the four amounts above which the 35, 50, 65 and 80 percent tiers
    begin, and the amount at which the 85 percent tier begins, each adjusted
    under 42 U.S.C. 1395r(i)(5): increased by the percentage (if any) by which
    average CPI-U for the 12 months ending August of the preceding year
    exceeds its base-period average, then rounded to the nearest $1,000.
    """
    if year < MEDICARE_IRMAA_FIRST_INDEXED_YEAR:
        raise ValueError(
            f"1395r(i)(5) adjusts against August 2018 only from "
            f"{MEDICARE_IRMAA_FIRST_INDEXED_YEAR}; got {year}."
        )
    window = get_cpi_u_average_for_12_months_ending_august(parameters, year - 1)

    def adjust(amount: int, base_year: int) -> float:
        base = get_cpi_u_average_for_12_months_ending_august(parameters, base_year)
        return round_medicare_irmaa_amount(amount * (1 + max(window / base - 1, 0)))

    lower = tuple(
        adjust(amount, MEDICARE_IRMAA_CPI_BASE_YEAR)
        for amount in MEDICARE_IRMAA_STATUTORY_AMOUNTS
    )
    if year < MEDICARE_IRMAA_TOP_FIRST_INDEXED_YEAR:
        top = float(MEDICARE_IRMAA_STATUTORY_TOP_AMOUNT)
    else:
        top = adjust(
            MEDICARE_IRMAA_STATUTORY_TOP_AMOUNT, MEDICARE_IRMAA_TOP_CPI_BASE_YEAR
        )
    return lower, top


def get_medicare_irmaa_thresholds(
    lower: Tuple[float, ...], top: float
) -> Dict[str, Tuple[float, ...]]:
    """Bracket thresholds of each filing status's IRMAA scale.

    The first four tiers cover income "more than" a dollar amount and the top
    tier income of "at least" its amount (42 U.S.C. 1395r(i)(3)(C)(i)(III)).
    A bracket applies from its threshold, so, as in the published years, the
    first four thresholds sit $1 above their amounts.
    """
    if lower[3] - lower[0] >= lower[0]:
        raise ValueError(
            "The married filing separately scale assumes its 80 percent tier "
            "starts below the unmarried threshold amount."
        )
    unmarried = (0, *(amount + 1 for amount in lower), top)
    return {
        "single": unmarried,
        "head_of_household": unmarried,
        "surviving_spouse": unmarried,
        # (C)(ii): twice the unmarried amounts for the calendar year, but 150 percent
        # of the unmarried top amount for the calendar year (the $500,000 amount as
        # adjusted under (5)(C)). Under (5)(B), the Secretary rounds only amounts
        # increased under (A) or (C).
        "joint": (0, *(2 * amount + 1 for amount in lower), 1.5 * top),
        # (C)(iii): each amount less the unmarried threshold amount, with no
        # adjustment at or below that threshold ((i)(1)).
        "separate": (0, lower[0] + 1, top - lower[0]),
    }


def extend_medicare_irmaa_thresholds(parameters: ParameterNode, end_year: int) -> None:
    """Project the Medicare Part B and Part D IRMAA income thresholds.

    Part D uses the Part B thresholds (42 U.S.C. 1395w-113(a)(7)(A) and
    (B)(i)(I)). Each year after the last CMS-published one is computed from
    the statutory amounts (see ``get_medicare_irmaa_unmarried_amounts``)
    rather than chained from the prior year's rounded values. CMS values
    encoded in the YAML take precedence for their own years.
    """
    medicare = parameters.gov.hhs.medicare
    thresholds_by_year = {}
    for program in (medicare.part_b, medicare.part_d):
        for name, scale in program.irmaa.children.items():
            if name not in MEDICARE_IRMAA_APPLICABLE_PERCENTAGES:
                raise ValueError(f"Unexpected Medicare IRMAA scale: {name}.")
            for index, bracket in enumerate(scale.brackets):
                threshold = bracket.threshold
                first_projected_year = 1 + max(
                    int(value.instant_str[:4]) for value in threshold.values_list
                )
                for year in range(first_projected_year, end_year + 1):
                    if year not in thresholds_by_year:
                        thresholds_by_year[year] = get_medicare_irmaa_thresholds(
                            *get_medicare_irmaa_unmarried_amounts(parameters, year)
                        )
                    year_thresholds = thresholds_by_year[year][name]
                    if len(year_thresholds) != len(scale.brackets):
                        raise ValueError(
                            f"Expected {len(year_thresholds)} brackets in the "
                            f"{name} Medicare IRMAA scale; found "
                            f"{len(scale.brackets)}."
                        )
                    threshold.update(
                        period=f"year:{year}-01-01:1",
                        value=float(year_thresholds[index]),
                    )
                threshold.update(
                    start=instant(f"{end_year}-01-01"),
                    value=threshold(f"{end_year}-01-01"),
                )


def get_medicare_part_d_irmaa_amount(
    base_beneficiary_premium: float,
    applicable_percentage: float,
    base_percent: float,
) -> float:
    """One Part D income-related monthly adjustment amount.

    42 U.S.C. 1395w-113(a)(7)(B): the base beneficiary premium times the
    applicable percentage less the base beneficiary premium percent, divided
    by that percent. CMS publishes the amounts to the nearest 10 cents.
    """
    premium = Decimal(repr(base_beneficiary_premium))
    applicable = Decimal(repr(applicable_percentage))
    base = Decimal(repr(base_percent))
    amount = premium * (applicable - base) / base
    return float(amount.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def extend_medicare_part_d_irmaa_amounts(
    parameters: ParameterNode, end_year: int
) -> None:
    """Project the Medicare Part D income-related monthly adjustment amounts.

    Each year after the last CMS-published one applies 42 U.S.C.
    1395w-113(a)(7)(B) to the Medicare Trustees' projected base beneficiary
    premium. The base beneficiary premium percent falls from 25.5 percent to
    the (a)(9) percent in 2030, which raises every amount; the Trustees
    expect 20 percent. CMS values encoded in the YAML take precedence for
    their own years.
    """
    base_beneficiary_premium = parameters.calibration.gov.hhs.cms.medicare_part_d_base_beneficiary_premium_per_enrollee
    part_d = parameters.gov.hhs.medicare.part_d
    for name, scale in part_d.irmaa.children.items():
        applicable_percentages = MEDICARE_IRMAA_APPLICABLE_PERCENTAGES.get(name)
        if applicable_percentages is None or len(applicable_percentages) != len(
            scale.brackets[1:]
        ):
            raise ValueError(
                f"Unexpected Medicare Part D IRMAA scale or bracket count: {name}."
            )
        for bracket, applicable_percentage in zip(
            scale.brackets[1:], applicable_percentages
        ):
            amount = bracket.amount
            first_projected_year = 1 + max(
                int(value.instant_str[:4]) for value in amount.values_list
            )
            for year in range(first_projected_year, end_year + 1):
                period = f"{year}-01-01"
                amount.update(
                    period=f"year:{period}:1",
                    value=get_medicare_part_d_irmaa_amount(
                        base_beneficiary_premium(period),
                        applicable_percentage,
                        part_d.base_beneficiary_premium_percent(period),
                    ),
                )
            amount.update(
                start=instant(f"{end_year}-01-01"),
                value=amount(f"{end_year}-01-01"),
            )


def long_range_growth_rate(
    year: int,
    last_projected_year: int,
    short_range_growth: float,
    long_range_growth: Dict[int, float],
) -> float:
    """Annual growth rate for a year after the last projected year, on a path
    that glides from the short-range rate to long-range rates.

    The knots are (last_projected_year, short_range_growth) and each
    (year, rate) in long_range_growth. The Medicare Trustees interpolate
    between their short-range and long-range rates; this path is linear
    between adjacent knots, and holds the last knot's rate after it.
    """
    knots = sorted(long_range_growth.items())
    if not knots or knots[0][0] <= last_projected_year:
        raise ValueError("Long-range growth knots must follow the last projected year.")
    if year <= last_projected_year:
        raise ValueError(
            "Long-range growth applies only after the last projected year."
        )
    previous_year, previous_rate = last_projected_year, short_range_growth
    for knot_year, knot_rate in knots:
        if year == knot_year:
            return knot_rate
        if year < knot_year:
            share = (year - previous_year) / (knot_year - previous_year)
            return previous_rate + share * (knot_rate - previous_rate)
        previous_year, previous_rate = knot_year, knot_rate
    return previous_rate


def extend_parameter_values(
    parameter: Parameter,
    last_projected_year: int,
    end_year: int,
    period_month: int = 1,
    period_day: int = 1,
    growth_years: Optional[Tuple[int, int]] = None,
    long_range_growth: Optional[Dict[int, float]] = None,
) -> None:
    """
    Extend a parameter's values from last_projected_year to end_year. The
    short-range rate is the growth between growth_years (by default the last
    two projected years). It repeats in every year or, given
    long_range_growth, glides through the knots. Years after end_year hold
    its value.

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
        long_range_growth: Optional {year: annual growth rate} knots. When
            given, growth moves from the measured short-range rate, placed
            at last_projected_year, through the knots (see
            long_range_growth_rate) instead of repeating the short-range
            rate in every year.
    """
    # Measure the short-range growth rate between growth_years
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
        if long_range_growth is None:
            new_value = previous_value * growth_rate
        else:
            new_value = previous_value * (
                1
                + long_range_growth_rate(
                    year, last_projected_year, growth_rate - 1, long_range_growth
                )
            )
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
    *,
    cap: Optional[Parameter] = None,
) -> None:
    """
    Extend the Social Security contribution and benefit base through `end_year`.

    Follows 42 U.S.C. 430(b) on the projected national average wage index
    (NAWI): the base for year Y is the larger of the base in effect for Y - 1
    and the 1994 base ($60,600) times NAWI(Y - 2) / NAWI(1992), rounded to the
    nearest $300 (a multiple of $150 rounds up). 20 CFR 404.1048(b)(2)(i)
    still states the pre-1995 chained formula, which Pub. L. 103-296,
    sec. 321(g)(1), replaced for bases after 1994.

    `cap` defaults to `gov.irs.payroll.social_security.cap`. Pass another
    parameter that holds the base, such as a copy of it, to extend that
    parameter instead: the rule then reads its 1994 base and its value for
    Y - 1, and the NAWI.
    """
    if cap is None:
        cap = parameters.gov.irs.payroll.social_security.cap
    nawi = parameters.gov.ssa.nawi
    base_1994 = cap("1994-01-01")
    nawi_1992 = nawi("1992-01-01")

    for year in range(last_projected_year + 1, end_year + 1):
        current_cap = cap(f"{year - 1}-01-01")
        proposed_cap = round_social_security_payroll_cap(
            base_1994 * nawi(f"{year - 2}-01-01") / nawi_1992
        )
        cap.update(
            period=f"year:{year}-01-01:1",
            value=max(current_cap, proposed_cap),
        )

    final_value = cap(f"{end_year}-01-01")
    cap.update(start=instant(f"{end_year}-01-01"), value=final_value)


def extend_social_security_wage_indexed_parameters(
    parameters: ParameterNode,
    end_year: int,
    *,
    cap: Optional[Parameter] = None,
) -> None:
    """Extend SSA wage-indexed benefit parameters with statutory lag and rounding.

    The wage base for each year from 2027 is set to the contribution and
    benefit base. `cap` defaults to `gov.irs.payroll.social_security.cap`.
    Pass another parameter that holds the base, such as a copy of it, to read
    the wage base from that parameter instead, so a reform that changes only
    the payroll cap doesn't move the wage base when this runs after it.
    """
    ssa = parameters.gov.ssa
    social_security = ssa.social_security
    nawi = ssa.nawi

    wage_base = social_security.wage_base
    if cap is None:
        cap = parameters.gov.irs.payroll.social_security.cap
    qc_threshold = social_security.quarters_of_coverage_threshold
    earnings_test = social_security.earnings_test
    pia = social_security.pia.formula_factors
    sga = ssa.sga

    for year in range(2027, end_year + 1):
        period = f"year:{year}-01-01:1"
        determination_nawi = nawi(f"{year - 2}-01-01")

        wage_base.update(
            period=period,
            value=cap(f"{year}-01-01"),
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
    # 2036 averages chained CPI-U from August 2034 to July 2035 (see #9105);
    # the 2035 instant holds CBO's February 2026 calendar-2035 point.
    IRS_LAST_PROJECTED_YEAR = 2036

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

    # SNAP uprating (October values, last projection year 2036)
    extend_parameter_values(
        parameters.gov.usda.snap.uprating,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=10,
        period_day=1,
    )

    # SSA uprating (January values, last projection year 2036)
    extend_parameter_values(
        parameters.gov.ssa.uprating,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Social Security National Average Wage Index (January values, last
    # projection year 2034, the NAWI behind CBO's 2036 CBB). The payroll tax
    # contribution and benefit base is indexed to NAWI, so this must remain
    # available through the full long-run projection horizon.
    extend_parameter_values(
        parameters.gov.ssa.nawi,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Social Security payroll tax cap / contribution and benefit base is
    # derived from NAWI under statute and should not be extrapolated
    # independently.
    extend_social_security_payroll_cap(
        parameters,
        last_projected_year=2036,
        end_year=END_YEAR,
    )

    extend_social_security_wage_indexed_parameters(
        parameters,
        end_year=END_YEAR,
    )

    # HHS uprating for Head Start and Early Head Start spending (January
    # values, last projection year 2036)
    extend_parameter_values(
        parameters.gov.hhs.uprating,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # HHS poverty guideline uprating (January values). Each guideline year
    # holds the prior calendar year's CPI-U (42 U.S.C. 9902(2)), so CBO's last
    # point, calendar 2036, sits at the 2037 instant.
    extend_parameter_values(
        parameters.gov.hhs.fpg_uprating,
        last_projected_year=2037,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # CPI-U (February values, last projection year 2036). Each February
    # instant holds CBO's February 2026 calendar-year average for that year
    # (the "# YYYY value" comments name the tax year it feeds), so CBO's last
    # point, calendar 2036, sits at the 2036 instant.
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_u,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # Chained CPI-U (February values, last projection year 2036), as for CPI-U.
    extend_parameter_values(
        parameters.gov.bls.cpi.c_cpi_u,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # CPI-W (February values, last projection year 2036; quarterly
    # projections run through 2036Q4)
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_w,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=2,
        period_day=1,
    )

    # CPI-U medical care (calendar-year values, last CBO projection year
    # 2036). Long-term care insurance premium inputs use this as their
    # uprater.
    extend_parameter_values(
        parameters.gov.bls.cpi.cpi_u_medical_care,
        last_projected_year=2036,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Washington's millionaires tax deduction uses an odd-year October
    # adjustment schedule. Must run after the CPI-W extension above so the
    # determination dates are available through the projection horizon.
    extend_wa_millionaires_standard_deduction(parameters, end_year=END_YEAR)

    # ACA benchmark premium uprating (January values, last actual 2027).
    # The published 2026 actual is 25.8% above 2025 and 2027 is a further
    # 12.5%; keep long-run growth at the 2024-2025 trend so the jumps do not
    # compound.
    extend_parameter_values(
        parameters.gov.aca.benchmark_premium_uprating,
        last_projected_year=2027,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        growth_years=(2024, 2025),
    )

    # CMS per-capita out-of-pocket medical spending (January values, last
    # projection year 2034). Health expense inputs use this as their uprater.
    # Growth glides from CMS's 2033-2034 rate to the Medicare Trustees'
    # long-range per capita health spending rates, and later years hold the
    # 2100 value.
    extend_parameter_values(
        parameters.calibration.gov.hhs.cms.moop_per_capita,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        long_range_growth=HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    )

    # CMS employer-sponsored insurance premium per enrollee (January values,
    # last projection year 2034). Employer and employee premium inputs use
    # this as their uprater. Growth glides from CMS's 2033-2034 rate to the
    # Medicare Trustees' long-range per capita health spending rates, and
    # later years hold the 2100 value.
    extend_parameter_values(
        parameters.calibration.gov.hhs.cms.esi_premium_per_enrollee,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        long_range_growth=HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    )

    # CMS direct purchase insurance premium per enrollee (January values, last
    # projection year 2034). Premiums for plans bought directly use this as
    # their uprater. Like the ESI premium, growth glides from CMS's 2033-2034
    # rate to the Medicare Trustees' long-range per capita health spending
    # rates, and later years hold the 2100 value.
    extend_parameter_values(
        parameters.calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        long_range_growth=HEALTH_SPENDING_PER_CAPITA_LONG_RANGE_GROWTH,
    )

    # Medicare Part B standard monthly premium (January values, last Trustees
    # projection year 2035). Reported Part B premium inputs use this as their
    # uprater.
    extend_parameter_values(
        parameters.calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee,
        last_projected_year=2035,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
    )

    # Medicare Part A standard premium and inpatient hospital deductible, and
    # Part D base beneficiary premium (January values, last Trustees
    # projection year 2035). The Part A premiums, the deductible and the Part
    # D income-related adjustment amounts are computed from them below.
    for medicare_series in (
        parameters.calibration.gov.hhs.cms.medicare_part_a_premium_per_enrollee,
        parameters.calibration.gov.hhs.cms.medicare_part_a_deductible,
        parameters.calibration.gov.hhs.cms.medicare_part_d_base_beneficiary_premium_per_enrollee,
    ):
        extend_parameter_values(
            medicare_series,
            last_projected_year=2035,
            end_year=END_YEAR,
            period_month=1,
            period_day=1,
        )

    # Medicare Part A full and reduced premiums follow the Trustees' projected
    # standard premium extended above, with the reduced premium 45 percent
    # below the full one (42 U.S.C. 1395i-2(d)).
    extend_medicare_part_a_premiums(parameters, end_year=END_YEAR)

    # The Medicare Part A deductible follows the Trustees' projected
    # deductible extended above, rounded to $4 with midpoints rounded up
    # (42 U.S.C. 1395e(b)(1)).
    extend_medicare_part_a_deductible(parameters, end_year=END_YEAR)

    # Medicare IRMAA income thresholds follow 42 U.S.C. 1395r(i)(5)'s CPI-U
    # schedule (12 months ending August), computed from the statutory
    # amounts. Must run after the CPI-U extension above.
    extend_medicare_irmaa_thresholds(parameters, end_year=END_YEAR)

    # Medicare Part D income-related adjustment amounts follow 42 U.S.C.
    # 1395w-113(a)(7)(B) applied to the base beneficiary premium extended
    # above.
    extend_medicare_part_d_irmaa_amounts(parameters, end_year=END_YEAR)

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

    # CMS Medicare spending per enrollee (January values, last projection
    # year 2034), which Medicare cost variables read directly. Sequestration
    # cuts Medicare expenditures 2 percent through August 31, 2033 (2026
    # Medicare Trustees Report, file page 209); its end lifts 2033 and 2034
    # growth, and the Trustees' per-beneficiary growth falls from 6.6
    # percent in 2034 to 5.4 percent in 2035 (Table V.D1, file page 210).
    # So each year from 2035 to 2100 grows at the 2031-2032 rate, and later
    # years hold the 2100 value.
    extend_parameter_values(
        parameters.calibration.gov.hhs.medicare.per_capita_cost,
        last_projected_year=2034,
        end_year=END_YEAR,
        period_month=1,
        period_day=1,
        growth_years=(2031, 2032),
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

    # Louisiana's standard deduction and age-65 retirement income exemption
    # follow R.S. 47:294(B) and 47:44.1(A): the prior year's amount times the
    # prior calendar year's CPI-U increase. Must run after the CPI-U extension
    # above so projected Decembers are available.
    extend_la_cpi_u_indexed_amounts(parameters, end_year=END_YEAR)

    # Medicaid long-term care home equity limits, CMS's rounded CPI-U method
    extend_medicaid_home_equity_limits(parameters, end_year=END_YEAR)

    # Federal Medicaid CSRA bounds and MMMNA maximum use cumulative CPI-U
    # since September 1988, rather than chaining annual rounded changes.
    extend_medicaid_spousal_impoverishment_standards(parameters, end_year=END_YEAR)

    # The limits on a dependent's standard deduction follow 26 U.S.C.
    # 63(c)(4)'s chained CPI-U schedule, computed from the statutory 1987 and
    # 1997 bases. Must run after the Chained CPI-U extension above so
    # projected windows are available.
    extend_dependent_standard_deduction_parameters(parameters, end_year=END_YEAR)

    # The educator expense cap follows 26 U.S.C. 62(d)(3)'s chained CPI-U
    # schedule, computed from the statutory $250 and 2014 base year. Must run
    # after the Chained CPI-U extension above.
    extend_educator_expense_cap(parameters, end_year=END_YEAR)

    # The HSA contribution limits follow 26 U.S.C. 223(g)'s chained CPI-U
    # schedule (12 months ending March 31), computed from the statutory
    # $2,250 and $4,500 and the 1997 base year. Must run after the Chained
    # CPI-U and CPI-U extensions above so projected windows are available.
    extend_hsa_contribution_limits(parameters, end_year=END_YEAR)

    # NYC income tax elimination credit thresholds follow the Tax Law
    # § 1310(h)(1)(B)(iii) schedule (CPI-U for the 12 months ending August 31
    # over the 2024 index), computed from the statutory 2025 amounts. Must run
    # after the CPI-U extension above so projected windows are available.
    extend_nyc_income_tax_elimination_credit_thresholds(parameters, end_year=END_YEAR)

    return parameters
