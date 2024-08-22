from policyengine_us.model_api import *


class dc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=18"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=17"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # follows Calculation F in references
        # calculate US itemized deductions less state non-property taxes
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        # calculate DC itemized deductions before partial phase-out
        dc_itm_deds = itm_deds_less_salt + uncapped_property_taxes
        # apply partial phase-out of DC itemized deductions
        EXEMPT_ITEMS = [
            "medical_expense_deduction",
            "casualty_loss_deduction",
        ]
        exempt_deds = add(tax_unit, period, EXEMPT_ITEMS)
        nonexempt_deds = max_(0, dc_itm_deds - exempt_deds)
        dc_agi = add(tax_unit, period, ["dc_agi"])
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.dc.tax.income.deductions
        phase_out_start = p.itemized.phase_out.start[filing_status]
        excess_agi = max_(0, dc_agi - phase_out_start)
        phase_out_amount = excess_agi * p.itemized.phase_out.rate
        limited_nonexempt_deds = max_(0, nonexempt_deds - phase_out_amount)
        return exempt_deds + limited_nonexempt_deds
