from policyengine_us.model_api import *


class ia_cca_monthly_units(Variable):
    value_type = float
    entity = Person
    label = "Iowa CCA half-day units of care per month per child"
    definition_period = MONTH
    defined_for = "ia_cca_eligible_child"
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"

    def formula(person, period, parameters):
        # A unit of service is a half day of up to 5 hours of care per
        # 24-hour period, and a full day bills as two half-day units
        # (IAC 441-170.1; 170.4(7)"a" sets the half-day rate at the
        # provider's full-day rate divided by 2). When the care schedule is
        # known, units are counted per day: one unit for a day of up to
        # 5 hours, two units for a longer day. PolicyEngine has no
        # authorized-units input, so when only weekly hours are reported
        # the units are prorated over 5-hour blocks instead.
        hours_per_unit = parameters(period).gov.states.ia.hhs.cca.payment.hours_per_unit
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        days_per_week = person("childcare_days_per_week", period.this_year)
        weeks_per_month = WEEKS_IN_YEAR / MONTHS_IN_YEAR
        daily_hours = weekly_hours / where(days_per_week > 0, days_per_week, 1)
        units_per_day = select(
            [daily_hours <= 0, daily_hours <= hours_per_unit],
            [0, 1],
            default=2,
        )
        schedule_units = days_per_week * units_per_day * weeks_per_month
        prorated_units = weekly_hours * weeks_per_month / hours_per_unit
        return where(days_per_week > 0, schedule_units, prorated_units)
