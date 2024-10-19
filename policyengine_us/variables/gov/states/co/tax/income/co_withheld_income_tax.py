from policyengine_us.model_api import *


class co_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Colorado withheld income tax"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        # Colorado adopts federal taxable income, so use federal standard deduction.
        p_irs = parameters(period).gov.irs.deductions.standard
        standard_deduction = p_irs.amount["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        p = parameters(period).gov.states.co.tax.income
        return p.rate * reduced_agi
