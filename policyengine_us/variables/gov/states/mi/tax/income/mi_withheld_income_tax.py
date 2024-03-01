from policyengine_us.model_api import *


class mi_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Michigan withheld income tax"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.mi.tax.income
        # We apply the tier 3 standard deduction amount
        standard_deduction = p.deductions.standard.tier_three.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rate * reduced_employment_income
