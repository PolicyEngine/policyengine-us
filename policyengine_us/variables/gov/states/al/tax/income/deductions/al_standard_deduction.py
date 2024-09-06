from policyengine_us.model_api import *


class al_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama standard deduction"
    unit = USD
    # The Code of Alabama 1975 Section 40-18-15 (b)(4).
    documentation = "https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amount = p.amount.max[filing_status]
        increment = p.phase_out.increment[filing_status]
        min_amount = p.amount.min[filing_status]
        rate = p.phase_out.rate[filing_status]
        threshold = p.phase_out.threshold[filing_status]
        al_agi = tax_unit("al_agi", period)
        # No "or fraction thereof" clause, so use integer (floor) division rather than ceiling.
        excess_income = max_(0, al_agi - threshold)
        increments = excess_income // increment
        reduction = increments * rate

        return max_(base_amount - reduction, min_amount)
