from policyengine_us.model_api import *


class ar_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Arkansas withheld income tax"
    defined_for = StateCode.AR
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.ar.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        rate = p.rates.main.rate.calc(reduced_agi)
        return rate * reduced_agi
