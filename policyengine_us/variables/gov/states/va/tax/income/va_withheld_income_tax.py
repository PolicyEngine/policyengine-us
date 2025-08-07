from policyengine_us.model_api import *


class va_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Virginia withheld income tax"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.va.tax.income
        standard_deduction = p.deductions.standard["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        return p.rates.calc(reduced_agi)
