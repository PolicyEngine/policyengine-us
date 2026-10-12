"""Supplemental Security Income timing helpers.

SSI monthly payments are due on the first day of the month and move to the
prior business day when that day is a weekend or legal holiday:
https://www.ssa.gov/OP_Home/cfr20/416/416-0502.htm

SSA budget tables present SSI federal obligations on a payment-date basis:
https://www.ssa.gov/oact/ssir/SSI24/IV_C_Payments.html
"""

from datetime import date, timedelta


def _as_fiscal_year(year) -> int:
    return int(str(year)[:4])


def _is_new_years_day_observed(day: date) -> bool:
    new_years_day = date(day.year, 1, 1)
    next_new_years_day = date(day.year + 1, 1, 1)
    return (
        day == new_years_day
        or (new_years_day.weekday() == 6 and day == date(day.year, 1, 2))
        or (next_new_years_day.weekday() == 5 and day == date(day.year, 12, 31))
    )


def _is_labor_day(day: date) -> bool:
    return day.month == 9 and day.weekday() == 0 and day.day <= 7


def _is_federal_holiday_affecting_ssi_payment(day: date) -> bool:
    return _is_new_years_day_observed(day) or _is_labor_day(day)


def ssi_payment_date(year: int, month: int) -> date:
    """Return the payment date for an SSI benefit month."""
    payment_date = date(year, month, 1)
    while payment_date.weekday() >= 5 or _is_federal_holiday_affecting_ssi_payment(
        payment_date
    ):
        payment_date -= timedelta(days=1)
    return payment_date


def ssi_benefit_months_for_federal_fiscal_year(year) -> tuple[date, ...]:
    """Return benefit months whose SSI payment dates fall in a federal FY."""
    fiscal_year = _as_fiscal_year(year)
    fiscal_year_start = date(fiscal_year - 1, 10, 1)
    fiscal_year_end = date(fiscal_year, 9, 30)

    benefit_months = []
    for calendar_year in (fiscal_year - 1, fiscal_year):
        for month in range(1, 13):
            payment_day = ssi_payment_date(calendar_year, month)
            if fiscal_year_start <= payment_day <= fiscal_year_end:
                benefit_months.append(date(calendar_year, month, 1))

    return tuple(benefit_months)


def ssi_benefit_months_for_calendar_year(year) -> tuple[date, ...]:
    """Return benefit months whose SSI payment dates fall in a calendar year."""
    calendar_year = _as_fiscal_year(year)
    calendar_year_start = date(calendar_year, 1, 1)
    calendar_year_end = date(calendar_year, 12, 31)

    benefit_months = []
    for benefit_year in (calendar_year, calendar_year + 1):
        for month in range(1, 13):
            payment_day = ssi_payment_date(benefit_year, month)
            if calendar_year_start <= payment_day <= calendar_year_end:
                benefit_months.append(date(benefit_year, month, 1))

    return tuple(benefit_months)


def ssi_calendar_year_payment_count(year) -> int:
    """Return SSI payment count for a calendar year."""
    return len(ssi_benefit_months_for_calendar_year(year))


def ssi_federal_fiscal_year_payment_count(year) -> int:
    """Return SSI payment count for a federal fiscal year."""
    return len(ssi_benefit_months_for_federal_fiscal_year(year))


def ssi_benefit_months_for_federal_fiscal_year_in_calendar_year(
    fiscal_year,
    calendar_year=None,
) -> tuple[date, ...]:
    """Return fiscal-year SSI benefit months available in one calendar year."""
    resolved_calendar_year = (
        _as_fiscal_year(fiscal_year)
        if calendar_year is None
        else _as_fiscal_year(calendar_year)
    )
    return tuple(
        benefit_month
        for benefit_month in ssi_benefit_months_for_federal_fiscal_year(fiscal_year)
        if benefit_month.year == resolved_calendar_year
    )


def ssi_federal_fiscal_year_payment_count_in_calendar_year(
    fiscal_year,
    calendar_year=None,
) -> int:
    """Return fiscal-year SSI payment count represented in one calendar year."""
    return len(
        ssi_benefit_months_for_federal_fiscal_year_in_calendar_year(
            fiscal_year,
            calendar_year,
        )
    )
