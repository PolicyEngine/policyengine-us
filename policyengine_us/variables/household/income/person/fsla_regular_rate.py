from policyengine_us.model_api import *


class fsla_regular_rate(Variable):
    value_type = float
    entity = Person
    label = "regular hourly rate for FLSA overtime"
    documentation = (
        "Reconciles weekly hours with annual employment income for FLSA overtime "
        "calculations. ORG-backed hourly wage is a fallback when annual earnings "
        "and hours cannot identify a regular rate."
    )
    unit = USD
    definition_period = YEAR

    def formula_2014(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        worked_hours = person("hours_worked_last_week", period)
        employment_income = person("employment_income", period)
        is_paid_hourly = person("is_paid_hourly", period)
        hourly_wage = person("hourly_wage", period)

        weekly_overtime_hours = max_(worked_hours - p.hours_threshold, 0)
        weekly_straight_time_hours = min_(max_(worked_hours, 0), p.hours_threshold)
        straight_time_equivalent_hours = WEEKS_IN_YEAR * (
            weekly_straight_time_hours + weekly_overtime_hours * p.rate_multiplier
        )
        employment_income_rate = employment_income / max_(
            straight_time_equivalent_hours, 1
        )
        employment_income_rate_available = (employment_income > 0) & (
            straight_time_equivalent_hours > 0
        )
        hourly_wage_available = is_paid_hourly & (hourly_wage > 0)

        return where(
            employment_income_rate_available,
            employment_income_rate,
            where(hourly_wage_available, hourly_wage, 0),
        )
