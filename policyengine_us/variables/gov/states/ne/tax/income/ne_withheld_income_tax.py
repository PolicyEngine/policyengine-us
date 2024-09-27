from policyengine_us.model_api import *


class ne_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Nebraska withheld income tax"
    defined_for = StateCode.NE
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.ne.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.base_amount["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        return p.rates.single.calc(reduced_agi)
