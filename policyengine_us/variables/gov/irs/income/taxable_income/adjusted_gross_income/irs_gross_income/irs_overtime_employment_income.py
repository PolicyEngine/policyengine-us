from policyengine_us.model_api import *


class irs_overtime_employment_income(Variable):
    value_type = float
    entity = Person
    label = "IRS overtime employment income"
    unit = USD
    documentation = (
        "Amount of employment income that can be attributed to overtime work."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        hours_worked = person("weekly_hours_worked", period) * 52
        overtime_hours = person("weekly_overtime_hours", period) * 52
        overtime_percentage = np.zeros_like(hours_worked)
        mask = hours_worked != 0
        overtime_percentage[mask] = overtime_hours[mask] / hours_worked[mask]
        return employment_income * overtime_percentage
