from policyengine_us.model_api import *


class nh_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire withheld income tax"
    defined_for = StateCode.NH
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.nh.tax.income
        # Since New Hampshire does not have a standard deduction
        # we apply the base personal exemption amount
        personal_exemptions = p.exemptions.amount.base["SINGLE"]
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.rate * reduced_employment_income
