from policyengine_us.model_api import *


class nh_fanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
        "https://www.dhhs.nh.gov/fam_htm/html/603_01_earned_income_disregards_eid_fam.htm",
        "https://www.dhhs.nh.gov/famar_htm/html/603_01_earned_income_disregards_eid_sr_97-03_02_97_fam_a.htm",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # Countable earned income for the benefit amount. Per He-W 654.13(d)
        # and (e), the 50% disregard applies to the benefit of every eligible
        # unit, including applicants who passed the 20% eligibility test.
        # Note: The Cliff Effect Initiative's two-year pilot (October 2022 to
        # September 2024) gave a 75% disregard to participants who started or
        # moved to full-time work, and 100% for high-demand jobs with medical
        # benefits. It is not implemented, because the inputs do not identify
        # the pilot group or the job classification.
        p = parameters(period).gov.states.nh.dhhs.fanf.income.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        after_disregard = gross_earned * (1 - p.recipient_rate)

        # Child care deduction applies to earned income (He-W 654.02(b)(3))
        child_care_deduction = spm_unit("nh_fanf_child_care_deduction", period)
        return max_(after_disregard - child_care_deduction, 0)
