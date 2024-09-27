from policyengine_us.model_api import *


class vt_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Vermont withheld income tax"
    defined_for = StateCode.VT
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.vt.tax.income
        # We apply the base standard deduction amount
        personal_exmptions = p.deductions.standard.base["SINGLE"]
        reduced_agi = max_(agi - personal_exmptions, 0)
        return p.rates.single.calc(reduced_agi)
