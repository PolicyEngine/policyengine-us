from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/montana-code/title-15-taxation/chapter-30-individual-income-tax/part-21-rate-and-general-provisions/section-15-30-2131-repealed-effective-112024-temporary-deductions-allowed-in-computing-net-income"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        eligible_children = person.tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_children",
            period,
        )  # Line 1
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        cap = p.cap.calc(eligible_children)
        care_expenses = person.tax_unit("tax_unit_childcare_expenses", period)
        capped_expenses = min_(care_expenses, cap)  # Line 2
        agi = person("mt_agi", period)  # Line 3
        reduction = p.phase_out.calc(agi)  # Line 6
        # The deduction has to be allocated equally between spouses
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * (max_(0, capped_expenses - reduction) / 0.5)
