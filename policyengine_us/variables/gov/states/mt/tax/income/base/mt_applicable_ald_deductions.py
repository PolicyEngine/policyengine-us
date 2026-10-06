from policyengine_us.model_api import *


class mt_applicable_ald_deductions(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable above-the-line deductions "
    unit = USD
    documentation = (
        "Each spouse's own federal adjustments to income, for their column of "
        "the Taxable Social Security Benefits Schedule (Form 2, line 7, before "
        "removing student loan interest)."
    )
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # 2023 Form 2 instructions, page 6: deductions attributable to only one
        # spouse, the student loan interest deduction included, must be claimed
        # by that spouse.
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
        # MCA 15-30-2110(6) to (9) (2021), in force through tax year 2023.
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0100/0150-0300-0210-0100.html",
        # Taxable Social Security Benefits Schedule, line 7.
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=6",
    )

    def formula(person, period, parameters):
        # Items attributable to one spouse are claimed by that spouse (ARM
        # 42.15.206(1)); a joint net capital loss may be divided by ownership
        # (ARM 42.15.206(3)(a)), as above_the_line_deductions_person divides
        # it. MCA 15-30-2110(9)(a) also lets spouses split student loan
        # interest equally or by AGI; the instructions have each spouse claim
        # their own, which is what this uses.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * person("above_the_line_deductions_person", period)
