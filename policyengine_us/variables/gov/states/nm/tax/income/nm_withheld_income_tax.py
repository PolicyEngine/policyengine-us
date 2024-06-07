from policyengine_us.model_api import *


class nm_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "New Mexico withheld income tax"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p_irs = parameters(period).gov.irs.deductions.standard
        # We apply the base IRS standard deduction amount
        standard_deduction = p_irs.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        p = parameters(period).gov.states.nm.tax.income
        return p.main.single.calc(reduced_employment_income)
