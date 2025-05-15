from policyengine_us.model_api import *


class overtime_income(Variable):
    value_type = float
    entity = Person
    label = "Income from overtime hours worked"
    unit = USD
    definition_period = YEAR

    # This variable only exists for the purpose of the tax_exempt_reform

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        worked_hours = person("weekly_hours_worked", period)
        weekly_pay = person("employment_income", period) / WEEKS_IN_YEAR

        non_overtime_hourly_rate = weekly_pay / (
            p.hours_threshold
            + max_((worked_hours - p.hours_threshold), 0) * p.rate_multiplier
        )
        overtime_income = (
            max_((worked_hours - p.hours_threshold), 0)
            * non_overtime_hourly_rate
            * p.rate_multiplier
        )

        return overtime_income * WEEKS_IN_YEAR
