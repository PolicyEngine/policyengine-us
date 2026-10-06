from policyengine_us.model_api import *


class mt_casualty_loss_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana casualty and theft loss deduction on a joint return"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 15
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=35",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=36",
        # 2022 Form 4684, lines 10-12 and 17; IRS Publication 547, $100 Rule
        "https://www.irs.gov/pub/irs-prior/f4684--2022.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/p547--2022.pdf#page=10",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.casualty_loss.applies:
            return 0
        # The return completes one federal Form 4684, using its Montana
        # adjusted gross income in place of federal adjusted gross income.
        p_casualty = parameters(period).gov.irs.deductions.itemized.casualty
        # A joint return is one individual for the $100 rule. The model records
        # one loss amount per person, not separate casualty events, so the
        # return's losses are treated as one casualty and the $100 reduction
        # (Form 4684 line 11) applies once.
        loss = add(tax_unit, period, ["casualty_loss"])
        reduced_loss = max_(loss - p_casualty.per_casualty_reduction, 0)
        agi = tax_unit("mt_agi_joint", period)
        return p_casualty.active * max_(reduced_loss - agi * p_casualty.floor, 0)
