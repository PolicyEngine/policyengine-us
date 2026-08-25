from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://web.archive.org/web/20230914140156/https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        if not p.in_effect:
            return 0
        tax_unit = person.tax_unit
        members = tax_unit.members
        qualifying_individual = members(
            "mt_child_dependent_care_expense_deduction_qualifying_individual",
            period,
        )
        # Form 2441-M line 1
        qualifying_individuals = tax_unit.sum(qualifying_individual)
        qualifying_care_expenses = tax_unit.sum(
            members("care_expenses", period) * qualifying_individual
        )
        childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)
        total_expenses = childcare_expenses + qualifying_care_expenses
        # Form 2441-M line 2: the lesser of actual dependent care expenses
        # or the cap based on the number of qualifying individuals.
        capped_expenses = min_(total_expenses, p.cap.calc(qualifying_individuals))
        # Line 3
        agi = person("mt_agi_indiv", period)
        # Line 6
        reduction = p.phase_out.calc(agi)
        # The deduction has to be allocated equally between spouses
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * (max_(0, capped_expenses - reduction) * 0.5)
