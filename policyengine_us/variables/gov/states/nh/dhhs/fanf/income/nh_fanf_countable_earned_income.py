from policyengine_us.model_api import *


class nh_fanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire FANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.dhhs.nh.gov/famar_htm/html/603_01_earned_income_disregards_eid_sr_97-03_02_97_fam_a.htm",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
        "https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/tanf-state-plan.pdf#page=29",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # NH has different disregard rates for applicants (20%) vs recipients
        # Recipients: 50% (1997) → 75% (Sept 2022 Cliff Effect Initiative)
        # Note: A 100% disregard exists for high-demand jobs (per NH Workforce
        # Innovation Opportunities Act board) with medical benefits offered,
        # but this is not implemented due to lack of job classification data.
        p = parameters(
            period
        ).gov.states.nh.dhhs.fanf.income.earned_income_disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        is_enrolled = spm_unit("is_tanf_enrolled", period)
        disregard_rate = where(is_enrolled, p.recipient_rate, p.applicant_rate)
        after_disregard = gross_earned * (1 - disregard_rate)

        # Child care deduction applies to earned income (FAM 603.05)
        child_care_deduction = spm_unit("nh_fanf_child_care_deduction", period)
        return max_(after_disregard - child_care_deduction, 0)
