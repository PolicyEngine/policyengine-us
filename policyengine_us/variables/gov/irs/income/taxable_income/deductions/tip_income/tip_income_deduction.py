from policyengine_us.model_api import *


class tip_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tip income deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "tip_income_deduction_ssn_requirement_met"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        tip_income = person("tip_income", period)
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.tip_income
        start = p.phase_out.start[filing_status]
        agi_excess = max_(agi - start, 0)
        phase_out_amount = agi_excess * p.phase_out.rate
        total_tip_income = tax_unit.sum(tip_income)
        capped_tip_income = min_(p.cap, total_tip_income)
        return max_(0, capped_tip_income - phase_out_amount)
