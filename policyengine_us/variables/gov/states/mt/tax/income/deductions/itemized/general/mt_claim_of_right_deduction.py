from policyengine_us.model_api import *


class mt_claim_of_right_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana claim of right repayment deduction"
    unit = USD
    documentation = (
        "The person's part of the federal claim of right repayment deduction "
        "(Schedule A, line 16), which Montana allows as an itemized "
        "deduction: through 2023 on Form 2 itemized deductions line 18, and "
        "from 2024 within the federal itemized deductions on Form 2 line 2."
    )
    definition_period = YEAR
    reference = (
        "https://leg.mt.gov/bills/2023/HB0199/HB0109_X.pdf#page=17",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=39",
        # 2024 Form 2 instructions, line 2, Worksheet A line 1: "Enter your
        # total federal itemized deductions from Form 1040, line 12".
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        deducted = person.tax_unit("claim_of_right_deduction", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        repayment = max_(0, person("claim_of_right_repayment", period)) * head_or_spouse
        # Historical small-class repayments belong only in the floor-subject
        # pool, even when the federal aggregate model combines distinct classes.
        small_repayment = person("mt_misc_claim_of_right_repayment", period)
        nonfloor_repayment = max_(0, repayment - small_repayment)
        total = person.tax_unit.sum(nonfloor_repayment)
        # Allocate the allowed federal amount to its head/spouse payers once,
        # without exceeding their eligible nonfloor repayments.
        share = nonfloor_repayment / where(total > 0, total, 1)
        return min_(deducted, total) * share
