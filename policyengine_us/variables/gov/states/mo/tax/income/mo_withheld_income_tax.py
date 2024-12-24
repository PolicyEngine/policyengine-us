from policyengine_us.model_api import *


class mo_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Missouri withheld income tax"
    defined_for = StateCode.MO
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p_irs = parameters(period).gov.irs.deductions.standard
        # We apply the base IRS standard deduction amount
        standard_deduction = p_irs.amount["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        p = parameters(period).gov.states.mo.tax.income
        return p.rates.calc(reduced_agi)
