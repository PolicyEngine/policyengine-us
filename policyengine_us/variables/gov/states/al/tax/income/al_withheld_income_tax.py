from policyengine_us.model_api import *


class al_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Alabama withheld income tax"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        # Assigning the maximum standard deduction amount
        p = parameters(period).gov.states.al.tax.income
        standard__deduction = p.deductions.standard.amount.max["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard__deduction, 0
        )
        return p.rates.single.calc(reduced_employment_income)
