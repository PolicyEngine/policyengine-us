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
        tax_unit = person.tax_unit
        # Line 1
        eligible_children = tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_children",
            period,
        )
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        cap = p.cap.calc(eligible_children)
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        # Line 2
        capped_expenses = min_(care_expenses, cap)
        # Line 3
        agi = person("mt_agi", period)
        # Line 6
        reduction = p.phase_out.calc(agi)
        # The deduction has to be allocated equally between spouses
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * (max_(0, capped_expenses - reduction) * 0.5)
