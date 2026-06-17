from policyengine_us.model_api import *


class mt_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.201",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/CC23NonTANFActivity070718.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # CC 2-3: two-parent families need 120 activity hours/month total;
        # single-parent families need 60 work hours/month, or full-time
        # school/training (no work requirement), or part-time school plus 40
        # work hours/month. We don't track part-time vs full-time student
        # status at the moment, so the part-time-student + 40-work-hours
        # pathway is treated the same as full-time student. The teen-parent-
        # in-school no-work exception and the exclusion of disabled parents
        # from the minimum-hour computation are also not modeled (no per-parent
        # inputs).
        p = parameters(period).gov.states.mt.dphhs.ccap.eligibility.activity_hours
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        monthly_hours = (
            person("weekly_hours_worked", period.this_year)
            * WEEKS_IN_YEAR
            / MONTHS_IN_YEAR
        )
        is_full_time_student = person("is_full_time_student", period.this_year)

        parent_work_hours = spm_unit.sum(monthly_hours * is_parent)
        parent_count = spm_unit.sum(is_parent)
        full_time_student_parents = spm_unit.sum(is_parent & is_full_time_student)
        two_parent = parent_count > 1
        single_parent_is_full_time_student = full_time_student_parents > 0
        both_parents_full_time_students = full_time_student_parents == parent_count

        two_parent_eligible = (
            parent_work_hours >= p.two_parent
        ) | both_parents_full_time_students
        single_parent_eligible = (
            parent_work_hours >= p.single_parent
        ) | single_parent_is_full_time_student
        return where(two_parent, two_parent_eligible, single_parent_eligible)
