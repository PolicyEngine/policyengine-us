from policyengine_us.model_api import *


class overtime_income(Variable):
    value_type = float
    entity = Person
    label = "Income from overtime hours worked"
    unit = USD
    definition_period = YEAR

    # This variable only exists for the purpose of the tax_exempt_reform

    def formula(person, period, parameters):
        """Overtime income estimated on a weekly basis"""
        p = parameters(period).gov.irs.income.exemption.overtime
        worked_hours = person("weekly_hours_worked", period)
        weekly_pay = person("weekly_pay", period)

        non_overtime_hourly_rate = max(
            weekly_pay
            / (
                p.normal_hours
                + (worked_hours - p.normal_hours) * p.extra_salary_rate
            ),
            0,
        )
        overtime_pay = (
            (worked_hours - p.normal_hours)
            * non_overtime_hourly_rate
            * p.extra_salary_rate
        )  # weekly

        return overtime_pay * p.weeks_worked
