from policyengine_us.model_api import *


class ia_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Iowa withheld income tax"
    defined_for = StateCode.IA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.ia.tax.income
        # We apply the base standard deduction amount
        if p.deductions.standard.applies_federal:
            p_fed = parameters(period).gov.irs.deductions
            standard_deduction = p_fed.standard.amount["SINGLE"]
        else:
            standard_deduction = p.deductions.standard.amount["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        if p.rates.by_filing_status.active:
            return p.rates.by_filing_status.other.calc(reduced_agi)
        return p.rates.combined.calc(reduced_agi)
