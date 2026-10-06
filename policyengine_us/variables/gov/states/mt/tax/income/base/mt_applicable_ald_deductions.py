from policyengine_us.model_api import *


class mt_applicable_ald_deductions(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable above-the-line deductions "
    unit = USD
    documentation = (
        "Each spouse's own federal adjustments to income, for their column of "
        "the Taxable Social Security Benefits Schedule (Form 2, line 7, before "
        "removing student loan interest). Items attributable to one spouse "
        "are claimed by that spouse, and the capital loss deduction is "
        "divided under Montana's rule (mt_capital_loss_reallocation)."
    )
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # 2023 Form 2 instructions, page 5: deductions attributable to only one
        # spouse must be claimed by that spouse.
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=13",
        # MCA 15-30-2110(6) and (8) (2021): capital losses and the IRA
        # deduction of spouses who file separately.
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0100/0150-0300-0210-0100.html",
        # Taxable Social Security Benefits Schedule, line 7.
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=6",
    )

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # The capital loss deduction is divided under Montana's rule.
        deductions = person("above_the_line_deductions_person", period) - person(
            "mt_capital_loss_reallocation", period
        )
        return head_or_spouse * deductions
