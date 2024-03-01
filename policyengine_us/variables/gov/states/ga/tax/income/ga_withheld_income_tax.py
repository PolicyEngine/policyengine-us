from policyengine_us.model_api import *


class ga_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Georgia withheld income tax"
    defined_for = StateCode.GA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.ga.tax.income
        # We apply the base standard deduction amount
        personal_exemptions = p.deductions.standard.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - personal_exemptions, 0
        )
        return p.main.single.calc(reduced_employment_income)
