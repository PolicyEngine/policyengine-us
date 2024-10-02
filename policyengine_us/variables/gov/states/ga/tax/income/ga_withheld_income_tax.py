from policyengine_us.model_api import *


class ga_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Georgia withheld income tax"
    defined_for = StateCode.GA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.ga.tax.income
        # We apply the base standard deduction amount
        personal_exemptions = p.deductions.standard.amount["SINGLE"]
        reduced_agi = max_(agi - personal_exemptions, 0)
        return p.main.single.calc(reduced_agi)
