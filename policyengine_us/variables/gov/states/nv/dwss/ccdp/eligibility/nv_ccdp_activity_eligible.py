from policyengine_us.model_api import *


class nv_ccdp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on Purpose of Care activity"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=76"

    def formula(spm_unit, period, parameters):
        # MS 400 series: the applicant and every other required adult must be
        # in an approved Purpose of Care activity.
        #   - POC 420 (working) needs monetary compensation and sets no minimum
        #     hours, so earnings stand in for it.
        #   - POC 450 (student) needs six or more credit hours at an accredited
        #     college, which every full-time college student meets. We don't
        #     track credit hours, so part-time students use the input below.
        #   - POC 470 (disability) requires someone else to care for the child
        #     outside child care hours. A disabled caretaker is covered only
        #     when another caretaker works or studies, so a lone disabled
        #     caretaker is not.
        #   - meets_ccdf_activity_test covers what we don't model individually:
        #     POC 430 (job search), POC 460 (training), and the student and
        #     disability cases above that fall outside these proxies.
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
        # We don't track activity-hour verification or overlapping two-parent
        # schedules at the moment (MS 400 series), nor the job-search 90-day or
        # student/job-search funding-availability limits. Annual earnings mark
        # a caretaker as working in every month of the year.
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        is_working = (person("employment_income", period.this_year) > 0) | (
            person("self_employment_income", period.this_year) > 0
        )
        is_student = person("is_full_time_college_student", period.this_year)
        in_activity = is_working | is_student
        is_covered = in_activity | person("is_disabled", period.this_year)
        has_active_caretaker = spm_unit.any(is_caretaker & in_activity)
        has_uncovered_caretaker = spm_unit.any(is_caretaker & ~is_covered)
        modeled_activity = has_active_caretaker & ~has_uncovered_caretaker
        meets_activity_test = spm_unit("meets_ccdf_activity_test", period.this_year)
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        # Restrict the protective-care pathway to an nv_ccdp_eligible_child so a
        # non-eligible household member does not confer eligibility.
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        in_protective_care = is_eligible_child & (
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        has_protective_child = spm_unit.any(in_protective_care)
        return (
            modeled_activity
            | meets_activity_test
            | is_tanf_enrolled
            | is_homeless
            | has_protective_child
        )
