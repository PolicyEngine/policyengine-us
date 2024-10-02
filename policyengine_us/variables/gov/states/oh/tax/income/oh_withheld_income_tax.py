from policyengine_us.model_api import *


class oh_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Ohio withheld income tax"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.oh.tax.income
        exempt = p.agi_threshold > agi
        # Since Ohio does not have a standard deduction, we apply the
        # personal exemption amount based on employment income as opposed to AGI
        personal_exemptions = p.exemptions.personal.amount.calc(agi)
        reduced_agi = max_(agi - personal_exemptions, 0)
        return p.rates.calc(reduced_agi) * ~exempt
