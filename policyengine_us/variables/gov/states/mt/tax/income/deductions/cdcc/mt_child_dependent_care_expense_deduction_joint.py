from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction on a joint return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://web.archive.org/web/20230914140156/https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1",
        # 2022 Form 2 instructions, Itemized Deductions Schedule, line 14
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=35",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        if not p.in_effect:
            return 0
        # Form 2441-M line 2
        eligible_expenses = tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_expenses", period
        )
        # Line 3: the return's Montana adjusted gross income; lines 4-7.
        agi = tax_unit("mt_agi_joint", period)
        deduction = max_(eligible_expenses - p.phase_out.calc(agi), 0)
        # A married person filing on a separate form cannot take the deduction
        # (MCA 15-30-2131(1)(c)(vi)(A)).
        filing_status = tax_unit("filing_status", period)
        separate_form = filing_status == filing_status.possible_values.SEPARATE
        return deduction * ~separate_form
