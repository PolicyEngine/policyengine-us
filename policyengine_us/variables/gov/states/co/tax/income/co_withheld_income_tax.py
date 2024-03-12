from policyengine_us.model_api import *


class co_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Colorado withheld income tax"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        # Colorado adopts federal taxable income, so use federal standard deduction.
        p_irs = parameters(period).gov.irs.deductions.standard
        standard__deduction = p_irs.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard__deduction, 0
        )
        p = parameters(period).gov.states.co.tax.income
        return p.rate * reduced_employment_income
