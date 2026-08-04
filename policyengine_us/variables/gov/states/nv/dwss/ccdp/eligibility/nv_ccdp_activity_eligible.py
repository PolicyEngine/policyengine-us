from policyengine_us.model_api import *


class nv_ccdp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on Purpose of Care activity"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=76"

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
        #   - Protective services (State Plan Section 2.2; Manual CPS/Foster
        #     Group Set, MS 410) make a child needing care eligible regardless
        #     of caretaker activity, so a child in foster care or receiving/
        #     needing protective services satisfies the need-for-care test on
        #     its own (mirrors the nv_ccdp_copay protective-care waiver).
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
        # Restrict the protective-care pathway to an nv_ccdp_eligible_child so a
        # non-eligible household member does not confer eligibility.
        person = spm_unit.members
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        in_protective_care = is_eligible_child & (
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        has_protective_child = spm_unit.any(in_protective_care)
        return (
            meets_activity_test | is_tanf_enrolled | is_homeless | has_protective_child
        )
