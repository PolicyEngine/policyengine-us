from policyengine_us.model_api import *


class mn_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        base_amt = p.base_amount[filing_status]
        aged_blind_count = tax_unit("aged_blind_count", period)
        extra_amt = aged_blind_count * p.extra_amount[filing_status]
        return base_amt + extra_amt
