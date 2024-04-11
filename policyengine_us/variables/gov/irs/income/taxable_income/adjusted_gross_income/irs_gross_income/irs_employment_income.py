from policyengine_us.model_api import *


class irs_employment_income(Variable):
    value_type = float
    entity = Person
    label = "IRS employment income"
    unit = USD
    documentation = "Employment income less payroll deductions."
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        pre_tax_contributions = person("pre_tax_contributions", period)
        return max_(0, employment_income - pre_tax_contributions)
