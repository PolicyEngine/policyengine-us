from policyengine_us.model_api import *


class in_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Indiana withheld income tax"
    defined_for = StateCode.IN
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states["in"].tax.income
        # Since Indiana does not have a standard deduction, we apply the maximum
        # personal exemption amount
        personal_exemptions = p.exemptions.base.amount
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.agi_rate * reduced_employment_income
