from datetime import date

from policyengine_us.tools.ssi import (
    ssi_benefit_months_for_federal_fiscal_year,
    ssi_benefit_months_for_federal_fiscal_year_in_calendar_year,
    ssi_benefit_months_for_calendar_year,
    ssi_calendar_year_payment_count,
    ssi_federal_fiscal_year_payment_count,
    ssi_federal_fiscal_year_payment_count_in_calendar_year,
    ssi_payment_date,
)


def test_ssi_payment_date_moves_weekends_and_holidays_to_prior_business_day():
    assert ssi_payment_date(2024, 1) == date(2023, 12, 29)
    assert ssi_payment_date(2022, 1) == date(2021, 12, 30)
    assert ssi_payment_date(2025, 9) == date(2025, 8, 29)
    assert ssi_payment_date(2026, 2) == date(2026, 1, 30)


def test_ssi_federal_fiscal_year_benefit_months_cover_payment_year():
    assert ssi_federal_fiscal_year_payment_count(2024) == 11
    assert ssi_benefit_months_for_federal_fiscal_year(2024) == tuple(
        date(2023, month, 1) for month in range(11, 13)
    ) + tuple(date(2024, month, 1) for month in range(1, 10))

    assert ssi_federal_fiscal_year_payment_count(2025) == 12
    assert ssi_federal_fiscal_year_payment_count(2028) == 13
    assert ssi_federal_fiscal_year_payment_count(2029) == 11


def test_ssi_federal_fiscal_year_benefit_months_can_be_calendar_year_limited():
    assert ssi_federal_fiscal_year_payment_count_in_calendar_year(2024) == 9
    assert ssi_benefit_months_for_federal_fiscal_year_in_calendar_year(2024) == tuple(
        date(2024, month, 1) for month in range(1, 10)
    )

    assert ssi_federal_fiscal_year_payment_count_in_calendar_year(2028) == 10
    assert ssi_benefit_months_for_federal_fiscal_year_in_calendar_year(2028) == tuple(
        date(2028, month, 1) for month in range(1, 11)
    )


def test_ssi_calendar_year_benefit_months_cover_payment_year():
    assert ssi_calendar_year_payment_count(2024) == 12
    assert ssi_benefit_months_for_calendar_year(2024) == tuple(
        date(2024, month, 1) for month in range(2, 13)
    ) + (date(2025, 1, 1),)

    assert ssi_calendar_year_payment_count(2028) == 12
    assert ssi_benefit_months_for_calendar_year(2028) == tuple(
        date(2028, month, 1) for month in range(2, 13)
    ) + (date(2029, 1, 1),)
