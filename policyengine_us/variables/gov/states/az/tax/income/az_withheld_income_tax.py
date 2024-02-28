from policyengine_us.model_api import *


class az_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Arizona withheld income tax"
    defined_for = StateCode.AZ
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.az.tax.income
        standard__deduction = p.deductions.standard.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard__deduction, 0
        )
        return p.main.single.calc(reduced_employment_income)
