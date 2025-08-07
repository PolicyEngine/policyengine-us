from policyengine_us.model_api import *


class al_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Alabama withheld income tax"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        # Assigning the maximum standard deduction amount
        p = parameters(period).gov.states.al.tax.income
        standard_deduction = p.deductions.standard.amount.max["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        return p.rates.single.calc(reduced_agi)
