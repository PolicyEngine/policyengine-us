from policyengine_us.model_api import *


class va_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Virginia withheld income tax"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.va.tax.income
        standard_deduction = p.deductions.standard["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rates.calc(reduced_employment_income)
