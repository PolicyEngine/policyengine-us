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

        weekly_overtime_hours = max_(worked_hours - p.hours_threshold, 0)
        annual_overtime_hours = weekly_overtime_hours * WEEKS_IN_YEAR

        return (
            person("employment_income_last_year")
            * annual_overtime_hours
            * (p.rate_multiplier - 1)
        )
