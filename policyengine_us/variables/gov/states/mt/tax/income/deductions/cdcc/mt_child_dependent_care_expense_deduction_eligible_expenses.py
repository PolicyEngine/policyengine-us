from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_eligible_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child and dependent care expenses eligible for the deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://web.archive.org/web/20230914140156/https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        person = tax_unit.members
        qualifying_individual = person(
            "mt_child_dependent_care_expense_deduction_qualifying_individual",
            period,
        )
        # Form 2441-M line 1
        qualifying_individuals = tax_unit.sum(qualifying_individual)
        qualifying_care_expenses = tax_unit.sum(
            person("care_expenses", period) * qualifying_individual
        )
        childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)
        total_expenses = childcare_expenses + qualifying_care_expenses
        # Form 2441-M line 2: the lesser of actual dependent care expenses
        # or the cap based on the number of qualifying individuals.
        return min_(total_expenses, p.cap.calc(qualifying_individuals))
