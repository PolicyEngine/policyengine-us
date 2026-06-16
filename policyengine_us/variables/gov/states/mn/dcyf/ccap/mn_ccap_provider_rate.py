from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mn.dcyf.ccap.mn_ccap_provider_type import (
    MNCCAPProviderType,
)
from policyengine_us.variables.gov.states.mn.dcyf.ccap.mn_ccap_rate_unit import (
    MNCCAPRateUnit,
)


class mn_ccap_provider_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Minnesota CCAP maximum monthly provider rate per child"
    definition_period = MONTH
    defined_for = "mn_ccap_eligible_child"
    reference = (
        # DHS-6441F standard maximum rates.
        "https://edocs.dhs.state.mn.us/lfserver/Public/DHS-6441F-ENG#page=5",
        # Minn. Stat. 142E.17 subd. 1(f), 2(b) — daily and weekly payment caps.
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.rates
        provider_type = person("mn_ccap_provider_type", period)
        age_group = person("mn_ccap_age_group", period)
        rate_unit = person("mn_ccap_rate_unit", period)
        # defined_for filters output but does not short-circuit vectorized
        # execution, so mask on Minnesota before indexing county_str; non-MN
        # county strings are absent from the rate tables and would crash the
        # lookup.
        county = person.household("county_str", period.this_year)
        in_mn = person.household("state_code_str", period.this_year) == "MN"
        county_key = where(in_mn, county, "HENNEPIN_COUNTY_MN")

        # Centers and license-exempt programs (paid at the center rate per
        # section 9.9) use the child care center column; family child care
        # providers use the family child care column. Legal non-licensed
        # providers use their own hourly rate table.
        family = MNCCAPProviderType.FAMILY_CHILD_CARE.name
        center = MNCCAPProviderType.CHILD_CARE_CENTER.name
        uses_center = (provider_type == MNCCAPProviderType.CHILD_CARE_CENTER) | (
            provider_type == MNCCAPProviderType.LICENSE_EXEMPT
        )

        weekly_rate = where(
            uses_center,
            p.weekly[center][age_group][county_key],
            p.weekly[family][age_group][county_key],
        )
        full_day_rate = where(
            uses_center,
            p.full_day[center][age_group][county_key],
            p.full_day[family][age_group][county_key],
        )
        hourly_rate = where(
            uses_center,
            p.hourly[center][age_group][county_key],
            p.hourly[family][age_group][county_key],
        )
        lnl_hourly_rate = p.lnl_hourly[age_group][county_key]

        hours_per_day = person("childcare_hours_per_day", period.this_year)
        hours_per_week = person("childcare_hours_per_week", period.this_year)
        days_per_month = person("childcare_attending_days_per_month", period.this_year)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR

        # Minn. Stat. 142E.17 subd. 1(f): payment for one day of care cannot
        # exceed the daily rate and payment for one week cannot exceed the
        # weekly rate. Cap the hourly rate at the daily rate per day, then cap
        # the week at the weekly rate.
        capped_daily = min_(hourly_rate * hours_per_day, full_day_rate)
        effective_hourly = where(
            hours_per_day > 0, capped_daily / hours_per_day, hourly_rate
        )
        weekly_from_hourly = min_(effective_hourly * hours_per_week, weekly_rate)
        monthly_hourly = weekly_from_hourly * weeks_per_month

        # A week of full-day care cannot exceed the weekly rate.
        monthly_full_day = min_(
            full_day_rate * days_per_month, weekly_rate * weeks_per_month
        )
        monthly_weekly = weekly_rate * weeks_per_month

        # Subd. 2(b): legal non-licensed providers are paid hourly, capped at
        # the maximum payable hours per day and per week.
        lnl_daily_fraction = where(
            hours_per_day > p.lnl_max_daily_hours,
            p.lnl_max_daily_hours / hours_per_day,
            1,
        )
        lnl_weekly_hours = min_(
            hours_per_week * lnl_daily_fraction, p.lnl_max_weekly_hours
        )
        monthly_lnl = lnl_hourly_rate * lnl_weekly_hours * weeks_per_month

        return select(
            [
                rate_unit == MNCCAPRateUnit.WEEKLY,
                rate_unit == MNCCAPRateUnit.FULL_DAY,
                rate_unit == MNCCAPRateUnit.LNL_HOURLY,
            ],
            [
                monthly_weekly,
                monthly_full_day,
                monthly_lnl,
            ],
            default=monthly_hourly,
        )
