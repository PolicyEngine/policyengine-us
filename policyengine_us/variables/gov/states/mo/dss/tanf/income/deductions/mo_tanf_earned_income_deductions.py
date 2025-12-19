from policyengine_us.model_api import *


class mo_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Missouri TANF earned income deductions for Percentage of Need test"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Note: Missouri has time-limited earned income disregards ($30+1/3 for
        # first 4 months, $30-only for next 8 months, 2/3 for up to 12 months).
        # This simplified implementation does not model these month limits.
        p = parameters(period).gov.states.mo.dss.tanf.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        work_expense = min_(gross_earned, p.amount)
        child_care = spm_unit("mo_tanf_child_care_deduction", period)
        after_work_expense = max_(gross_earned - p.amount, 0)
        two_thirds = after_work_expense * p.two_thirds_disregard.percentage
        thirty_one_third = where(
            gross_earned > 0,
            p.thirty_plus_one_third.flat_amount
            + after_work_expense * p.thirty_plus_one_third.percentage,
            0,
        )
        earned_disregard = where(is_enrolled, two_thirds, thirty_one_third)
        return work_expense + earned_disregard + child_care
