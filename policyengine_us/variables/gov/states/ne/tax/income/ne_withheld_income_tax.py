from policyengine_us.model_api import *


class ne_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Nebraska withheld income tax"
    defined_for = StateCode.NE
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.ne.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.base_amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rates.single.calc(reduced_employment_income)
