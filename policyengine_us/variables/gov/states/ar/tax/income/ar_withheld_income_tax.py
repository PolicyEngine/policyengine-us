from policyengine_us.model_api import *


class ar_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Arkansas withheld income tax"
    defined_for = StateCode.AR
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.ar.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        rate = p.rates.main.rate.calc(reduced_employment_income)
        return rate * reduced_employment_income
