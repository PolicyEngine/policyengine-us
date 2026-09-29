from policyengine_us.model_api import *


class mo_tanf_non_parent_caretaker_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF non-parent caretaker neediness budget income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-10/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # DSS Manual 0210.005.35: "Use the full need standard and do not
        # apply the $30 plus 1/3 and $30 disregards. Allow all expenses of
        # producing income." DSS Manual 0210.010.10 lists NPCR neediness as
        # a full-standard comparison, and its one example, which covers
        # both situations it lists, deducts the $90 standard work expense
        # and child care ($432 - $90 = $342 - $80 = $262). So both are
        # deducted here. This differs from the assistance unit's own
        # standard of need test (mo_tanf_income_for_need_test), where
        # 13 CSR 40-2.310(11) suspends those deductions; 0210.005.35's
        # "Allow all expenses of producing income" is specific to the
        # NPCR budget. The two-thirds disregard is not applied either. That
        # is an inference: 0210.005.35 names only the $30 plus 1/3 and $30
        # disregards, but the two-thirds disregard is not an expense of
        # producing income and applies only to Temporary Assistance
        # participants (13 CSR 40-2.310(9)(D)).
        p = parameters(period).gov.states.mo.dss.tanf
        person = spm_unit.members
        member = person("mo_tanf_non_parent_caretaker_budget_member", period)
        earned = person("tanf_gross_earned_income", period)
        # Mirrors mo_tanf_earned_income_deductions_person: a loss is not
        # reduced further by the work expense.
        work_expense = min_(earned, p.earned_income_disregard.amount)
        net_earned = spm_unit.sum((earned - work_expense) * member)
        # The child care is the unit's deduction: care for the children the
        # caretaker looks after, which the caretaker pays in order to work.
        child_care = spm_unit("mo_tanf_child_care_deduction", period)
        countable_earned = max_(net_earned - child_care, 0)
        unearned = add(person, period, p.income.sources.unearned)
        return countable_earned + spm_unit.sum(unearned * member)
