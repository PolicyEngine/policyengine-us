from policyengine_us.model_api import *


class fsla_overtime_premium(Variable):
    value_type = float
    entity = Person
    label = "premium income from overtime hours worked"
    unit = USD
    definition_period = YEAR
    defined_for = "is_eligible_for_fsla_overtime"

    def formula_2014(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        worked_hours = person("hours_worked_last_week", period)

        weekly_overtime_hours = max_(worked_hours - p.hours_threshold, 0)
        # Straight-time–equivalent hours in the year
        hour_equivalents = WEEKS_IN_YEAR * (
            p.hours_threshold + weekly_overtime_hours * p.rate_multiplier
        )
        # Implied straight-time hourly wage
        base_rate = person("employment_income", period) / hour_equivalents
        # Return only the overtime premium (e.g. the 50 % in time-and-a-half)
        return (
            base_rate
            * (p.rate_multiplier - 1)
            * weekly_overtime_hours
            * WEEKS_IN_YEAR
        )
