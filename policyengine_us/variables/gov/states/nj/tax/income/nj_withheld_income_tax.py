from policyengine_us.model_api import *


class nj_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "New Jersey withheld income tax"
    defined_for = StateCode.NJ
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.nj.tax.income
        # Since New Jersey does not have a standard deduction
        # we apply the regular personal exemption amount
        personal_exemptions = p.exemptions.regular.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.main.single.calc(reduced_employment_income)
