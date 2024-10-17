from policyengine_us.model_api import *


class irs_non_overtime_employment_income(Variable):
    value_type = float
    entity = Person
    label = "IRS non-overtime employment income"
    unit = USD
    documentation = (
        "Amount of employment income that does not include employment income."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        overtime_income = person("irs_overtime_employment_income", period)
        return max_(0, employment_income - overtime_income)
