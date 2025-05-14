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
        normal_hours = 40
        extra_salary_rate = 1.5
        worked_hours = person("weekly_hours_worked", period)
        weekly_pay = person("weekly_pay", period)
        # we need some assumption about the number of weeks worked in a year
        weeks_worked = 49  # or 52?

        non_overtime_hourly_rate = max(
            weekly_pay
            / (
                normal_hours
                + (worked_hours - normal_hours) * extra_salary_rate
            ),
            0,
        )
        overtime_pay = (
            (worked_hours - normal_hours)
            * non_overtime_hourly_rate
            * extra_salary_rate
        )  # weekly

        return overtime_pay * weeks_worked
