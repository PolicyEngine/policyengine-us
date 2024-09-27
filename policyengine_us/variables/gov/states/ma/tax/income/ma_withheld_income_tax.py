from policyengine_us.model_api import *


class ma_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts withheld income tax"
    defined_for = StateCode.MA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.ma.tax.income
        # Since Massachusetts does not have a standard deduction, we apply the
        # base personal exemption amount
        personal_exemption = p.exemptions.personal["SINGLE"]
        reduced_agi = max_(agi - personal_exemption, 0)
        return p.rates.part_b * reduced_agi
