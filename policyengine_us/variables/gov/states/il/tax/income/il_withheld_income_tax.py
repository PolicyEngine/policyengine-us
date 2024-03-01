from policyengine_us.model_api import *


class il_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Illinois withheld income tax"
    defined_for = StateCode.IL
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.il.tax.income
        # Since Illinois does not have a standard deduction
        # we apply the personal exemption amount
        personal_exemptions = p.exemption.personal
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.rate * reduced_employment_income
