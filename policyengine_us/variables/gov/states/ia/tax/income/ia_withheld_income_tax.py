from policyengine_us.model_api import *


class ia_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Iowa withheld income tax"
    defined_for = StateCode.IA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.ia.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rates.all.calc(reduced_employment_income)
