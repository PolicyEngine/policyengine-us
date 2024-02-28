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
        exempt = person.tax_unit("oh_income_tax_exempt", period)
        p = parameters(period).gov.states.oh.tax.income
        # Since Ohio does not have a standard deduction, we apply the  
        # personal exemption amount based on employment income as opposed to AGI
        personal_exemptions = p.exemptions.personal.amount.calc(employment_income)
        reduced_employment_income = max_(employment_income - personal_exemptions, 0)
        return p.rates.calc(reduced_employment_income) * ~exempt
