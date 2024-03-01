from policyengine_us.model_api import *


class vt_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Vermont withheld income tax"
    defined_for = StateCode.VT
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.vt.tax.income
        # We apply the base standard deduction amount
        personal_exmptions = p.deductions.standard.base["SINGLE"]
        reduced_employment_income = max_(
            employment_income - personal_exmptions, 0
        )
        return p.rates.single.calc(reduced_employment_income)
