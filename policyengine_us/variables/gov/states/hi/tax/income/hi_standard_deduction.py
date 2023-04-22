from policyengine_us.model_api import *


class hi_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii standard deduction"
    unit = USD
    # Hawaii Resident Income Tax Instructions pg.20
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amount = p.amount.max[filing_status]
        increment = p.phase_out.increment[filing_status]
        min_amount = p.amount.min[filing_status]
        rate = p.phase_out.rate[filing_status]
        threshold = p.phase_out.threshold[filing_status]
        al_agi = tax_unit("hi_agi", period)
        # No "or fraction thereof" clause, so use integer (floor) division rather than ceiling.
        excess_income = max(0, hi_agi - threshold)
        increments = excess_income // increment
        reduction = increments * rate

        return max(base_amount - reduction, min_amount)
