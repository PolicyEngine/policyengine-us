from policyengine_us.model_api import *


class nj_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "New Jersey withheld income tax"
    defined_for = StateCode.NJ
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.nj.tax.income
        # Since New Jersey does not have a standard deduction
        # we apply the regular personal exemption amount
        personal_exemptions = p.exemptions.regular.amount["SINGLE"]
        reduced_agi = max_(agi - personal_exemptions, 0)
        return p.main.single.calc(reduced_agi)
