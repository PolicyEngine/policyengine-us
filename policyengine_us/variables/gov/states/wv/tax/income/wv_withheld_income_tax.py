from policyengine_us.model_api import *


class wv_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "West Virginia withheld income tax"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.wv.tax.income
        # Since West Virginia does not have a standard deduction, we apply the maximum
        # personal exemption amount
        personal_exmptions = p.exemptions.base_personal + p.exemptions.personal
        reduced_agi = max_(agi - personal_exmptions, 0)
        return p.rates.single.calc(reduced_agi)
