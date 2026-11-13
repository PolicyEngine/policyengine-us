from policyengine_us.model_api import *


class mt_casualty_loss_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana casualty and theft loss deduction on a joint return"
    unit = USD
    definition_period = YEAR
    documentation = """
    PolicyEngine treats the head's and spouse's combined reported losses as one casualty and applies one per-casualty reduction.
    Taxpayers apply separate reductions to distinct events, which the
    available inputs cannot represent. The model has no input identifying
    disaster losses and retains the federal casualty activation flag.
    """
    reference = (
        # MCA § 15-30-2131(1)(a) (2021)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # 2015 Form 2, Schedule III line 20; PDF pages 27, 30
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2015_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=30",
        # 2017 Form 2, Schedule III line 20; PDF pages 27, 30
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2017_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=30",
        # PDF pages 35-36
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=35",
        # 2022 Form 4684, lines 10-12 and 17; IRS Publication 547, $100 Rule
        "https://www.irs.gov/pub/irs-prior/f4684--2022.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/p547--2022.pdf#page=10",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.casualty_loss.applies:
            return 0
        # The return figures its loss as on federal Form 4684 (lines 10-18),
        # using its Montana adjusted gross income in place of federal adjusted
        # gross income.
        # In 2022, Montana taxpayers may deduct only federally declared disaster
        # losses (line 15). The model cannot distinguish them, so it retains
        # the federal activation flag. No personal casualty loss is deductible while
        # gov.irs.deductions.itemized.casualty.active is false (from 2018).
        p_casualty = parameters(period).gov.irs.deductions.itemized.casualty
        # A joint return is one individual for the $100 rule. The model records
        # one loss amount per person, not separate casualty events, so the
        # return's losses are treated as one casualty and the $100 reduction
        # (Form 4684 line 11) applies once.
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return, as the dependent's income does:
        # adjusted_gross_income_person, and so Montana AGI, leaves it out.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        reduced_loss = max_(loss - p_casualty.per_casualty_reduction, 0)
        agi = tax_unit("mt_agi_joint", period)
        return p_casualty.active * max_(reduced_loss - agi * p_casualty.floor, 0)
