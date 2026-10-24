from policyengine_us.model_api import *


class ms_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2019/07/TANF-Manual-Revised_7.19.pdf#page=370",
        "https://www.mdhs.ms.gov/wp-content/uploads/2019/07/TANF-Manual-Revised_7.19.pdf#page=469",
    )

    def formula(spm_unit, period, parameters):
        # MDHS TANF Policy Manual, Volume III, pages 6025-6026: from the
        # monthly earned income of each individual, deduct (a) a standard
        # $90 for work expenses and then (b) the actual cost of care for
        # each dependent child or incapacitated adult in the budget.
        p = parameters(period).gov.states.ms.dhs.tanf.income.deductions
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        earned_after_work_expense = spm_unit.sum(max_(gross_earned - p.work_expense, 0))
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        dependent_care = childcare_expenses + adult_care_expenses
        return max_(earned_after_work_expense - dependent_care, 0)
