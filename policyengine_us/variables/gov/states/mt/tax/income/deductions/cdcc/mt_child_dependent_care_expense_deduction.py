from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The deduction in each filer's column: an unmarried filer's return, or "
        "each spouse's column when spouses file separately on the same form. "
        "A joint return uses mt_child_dependent_care_expense_deduction_joint."
    )
    reference = (
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://web.archive.org/web/20230914140156/https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1",
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 14
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=35",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        if not p.in_effect:
            return 0
        # Form 2441-M line 2
        eligible_expenses = person.tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_expenses", period
        )
        # Line 3: add the Montana adjusted gross income in columns A and B,
        # that is, the couple's combined income, not each spouse's own.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        combined_agi = person.tax_unit.sum(
            head_or_spouse * person("mt_agi_indiv", period)
        )
        # Lines 4-7
        deduction = max_(eligible_expenses - p.phase_out.calc(combined_agi), 0)
        # Spouses filing separately on the same form each enter one-half of
        # line 7 in their column; an unmarried filer enters all of it.
        married = person.tax_unit("tax_unit_married", period)
        head = person("is_tax_unit_head", period)
        share = where(married, head_or_spouse * 0.5, head * 1.0)
        # Married couples must file a joint return or file separately on the
        # same form (MCA 15-30-2131(1)(c)(vi)(A)); a spouse filing on a
        # separate form cannot take the deduction.
        filing_status = person.tax_unit("filing_status", period)
        separate_form = filing_status == filing_status.possible_values.SEPARATE
        return deduction * share * ~separate_form
