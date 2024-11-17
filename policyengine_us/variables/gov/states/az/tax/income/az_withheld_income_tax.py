from policyengine_us.model_api import *


class az_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Arizona withheld income tax"
    defined_for = StateCode.AZ
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.az.tax.income
        standard_deduction = p.deductions.standard.amount["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        return p.main.single.calc(reduced_agi)
