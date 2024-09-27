from policyengine_us.model_api import *


class mn_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Minnesota withheld income tax"
    defined_for = StateCode.MN
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.mn.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.base["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        return p.rates.single.calc(reduced_agi)
