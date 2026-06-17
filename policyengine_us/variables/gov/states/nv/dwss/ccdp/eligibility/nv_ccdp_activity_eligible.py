from policyengine_us.model_api import *


class nv_ccdp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on Purpose of Care activity"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/Child%20Care%20Manual%20July%202024.pdf#page=66"

    def formula(spm_unit, period, parameters):
        # MS 400 series: each required caretaker must be in an approved Purpose
        # of Care activity. Rather than re-deriving each POC category, we reuse
        # existing modeled status hooks:
        #   - meets_ccdf_activity_test covers POC 420 (working), 430 (job
        #     search), 450 (student), 460 (training), and 470 (disability of a
        #     caretaker where another adult is in an approved activity); it is a
        #     user input flagging that the responsible caretaker(s) participate
        #     in an approved activity.
        #   - is_tanf_enrolled covers POC 410 (TANF NEON referrals); using the
        #     enrollment input rather than computed TANF eligibility breaks the
        #     CCDP <-> TANF circular dependency.
        #   - is_homeless covers POC 440 (Homeless Self-Sufficiency Plan), a
        #     need-for-care reason that belongs inside the activity test.
        # POC 470 disability is intentionally NOT a standalone bypass: a lone
        # idle disabled caretaker is not activity-eligible (it requires another
        # adult in an approved activity), so the disability pathway flows
        # through meets_ccdf_activity_test rather than a bare is_disabled term.
        # We don't track activity-hour verification or overlapping two-parent
        # schedules at the moment (MS 400 series), nor the job-search 90-day or
        # student/job-search funding-availability limits.
        meets_activity_test = spm_unit("meets_ccdf_activity_test", period.this_year)
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return meets_activity_test | is_tanf_enrolled | is_homeless
