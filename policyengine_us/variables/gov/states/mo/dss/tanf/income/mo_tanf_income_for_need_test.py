from policyengine_us.model_api import *


class mo_tanf_income_for_need_test(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF income for Standard of Need test"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-10/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        work_expense = min_(gross_earned, p.amount)
        child_care = spm_unit("mo_tanf_child_care_deduction", period)
        countable_earned = max_(gross_earned - work_expense - child_care, 0)
        return countable_earned + gross_unearned
