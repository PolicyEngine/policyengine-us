from policyengine_us.model_api import *


class wv_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "West Virginia withheld income tax"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.va.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.base["SINGLE"]
        reduced_employment_income = max_(employment_income - standard_deduction, 0)
        return p.rates.single.calc(reduced_employment_income)
