from policyengine_us.model_api import *


class ma_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts withheld income tax"
    defined_for = StateCode.MA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.ma.tax.income
        # Since Massachusetts does not have a standard deduction, we apply the
        # base personal exemption amount
        personal_exemption = p.exemptions.personal["SINGLE"]
        reduced_employment_income = max_(
            employment_income - personal_exemption, 0
        )
        return p.rates.part_b * reduced_employment_income
