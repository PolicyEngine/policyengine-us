from policyengine_us.model_api import *


class nh_fanf_countable_earned_income_for_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF countable earned income for eligibility determination"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
        "https://www.dhhs.nh.gov/fam_htm/html/603_01_earned_income_disregards_eid_fam.htm",
        "https://www.dhhs.nh.gov/fam_htm/html/611_01_computing_eligibility_fam.htm",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # Per He-W 654.13(b) and (c), applicants who have not received FANF in
        # any of the previous 6 months use a 20% disregard to determine
        # eligibility. Per He-W 654.13(e)(1) and (2), recipients and applicants
        # who received FANF in that period use 50%.
        # NOTE: is_tanf_enrolled stands in for receipt in the previous 6 months,
        # so a former recipient who applies again gets the 20% rate here.
        p = parameters(period).gov.states.nh.dhhs.fanf.income.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        disregard_rate = where(is_enrolled, p.recipient_rate, p.applicant_rate)
        after_disregard = gross_earned * (1 - disregard_rate)

        # Child care deduction applies to earned income (He-W 654.02(b)(3))
        child_care_deduction = spm_unit("nh_fanf_child_care_deduction", period)
        return max_(after_disregard - child_care_deduction, 0)
