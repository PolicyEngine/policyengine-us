from policyengine_us.model_api import *


class mn_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.deductions
        # ... calculate pre-limitation amount
        filing_status = tax_unit("filing_status", period)
        base_amt = p.standard.base[filing_status]
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.standard.extra[filing_status]
        std_ded = base_amt + extra_amt
        # ... calculate standard deduction offset
        std_ded_offset = p.deduction_fraction * std_ded
        agi = tax_unit("adjusted_gross_income", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        excess_agi_offset = p.excess_agi_fraction * excess_agi
        offset = min_(std_ded_offset, excess_agi_offset)
        return max_(0, std_ded - offset)
