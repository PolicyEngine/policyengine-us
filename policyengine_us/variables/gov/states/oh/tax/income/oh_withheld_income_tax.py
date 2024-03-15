from policyengine_us.model_api import *


class oh_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Ohio withheld income tax"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.oh.tax.income
        exempt = p.agi_threshold > employment_income
        # Since Ohio does not have a standard deduction, we apply the
        # personal exemption amount based on employment income as opposed to AGI
        personal_exemptions = p.exemptions.personal.amount.calc(
            employment_income
        )
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.rates.calc(reduced_employment_income) * ~exempt
