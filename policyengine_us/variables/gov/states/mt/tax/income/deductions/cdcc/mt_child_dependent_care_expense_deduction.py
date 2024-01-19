from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/montana-code/title-15-taxation/chapter-30-individual-income-tax/part-21-rate-and-general-provisions/section-15-30-2131-repealed-effective-112024-temporary-deductions-allowed-in-computing-net-income"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        eligible_children = tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_children",
            period,
        )  # Line 1
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        cap = p.cap.calc(eligible_children)
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        capped_expenses = min_(care_expenses, cap)  # Line 2
        agi = tax_unit("mt_agi", period)  # Line 3
        reduction = p.phase_out.calc(agi)  # Line 6
        return max_(0, capped_expenses - reduction)
