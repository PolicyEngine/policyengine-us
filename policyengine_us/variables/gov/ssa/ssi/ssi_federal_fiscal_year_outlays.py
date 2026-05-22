from datetime import date, timedelta

from policyengine_us.model_api import *


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


def _ssi_payment_date(year: int, month: int) -> date:
    payment_date = date(year, month, 1)
    while payment_date.weekday() >= 5 or _is_federal_holiday_affecting_ssi_payment(
        payment_date
    ):
        payment_date -= timedelta(days=1)
    return payment_date


class ssi_federal_fiscal_year_outlays(Variable):
    value_type = float
    entity = Person
    label = "SSI federal fiscal year outlays"
    documentation = (
        "Supplemental Security Income payments assigned to the federal fiscal "
        "year in which they are paid."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # SSA presents SSI Federal Budget obligations on a payment-date
        # basis, with fiscal years covering October 1 through September 30.
        "https://www.ssa.gov/oact/ssir/SSI24/IV_C_Payments.html",
        # SSI payments are normally made on the first day of the month;
        # weekend or legal-holiday payments are made on the prior business day.
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0502.htm",
    )

    def formula(person, period, parameters):
        fiscal_year = period.start.year
        fiscal_year_start = date(fiscal_year - 1, 10, 1)
        fiscal_year_end = date(fiscal_year, 9, 30)
        total = 0

        # Include benefit months whose actual payment dates fall inside the
        # fiscal year. October payments can be shifted into September, so SSI
        # fiscal years can contain 11, 12, or 13 monthly payments.
        for month_offset in range(-3, 10):
            benefit_month = period.first_month.offset(month_offset, "month")
            payment_date = _ssi_payment_date(
                benefit_month.start.year,
                benefit_month.start.month,
            )
            paid_in_fiscal_year = fiscal_year_start <= payment_date <= fiscal_year_end
            if paid_in_fiscal_year:
                total += person("ssi", benefit_month)

        return total
