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
        # CC 2-3 Non-TANF Activity Requirements (CC23NonTANFActivity070718.pdf).
        # Work-hour thresholds: two-parent families need 120 combined work
        # hours/month; single-parent families need 60 work hours/month.
        #
        # A parent's work-hour obligation is WAIVED (they count as meeting the
        # activity test without work hours) when they are:
        #   - a full-time student: each full-time-student parent is individually
        #     excluded from the work-hour requirement, so a single student parent
        #     has no work requirement, a two-parent family with one student drops
        #     to the single-parent (60-hr) standard, and a two-parent family with
        #     both students has no work requirement ("no work requirement ... when
        #     both are attending school full time"). is_full_time_student includes
        #     K-12, so this also covers a teen parent attending high school/HiSET;
        #   - a parent with a disability who is unable to work ("Parent with a
        #     Disability"); we use is_disabled as a proxy for the ECSB
        #     "unable to work / unable to provide care" approval we don't track;
        #   - an incarcerated or pre-release parent in a two-parent ("intact")
        #     family ("the other parent must meet the ... 60 hours").
        # When one parent of a two-parent family is waived, the household drops to
        # the single-parent (60-hour) standard for the remaining parent; when all
        # parents are waived there is no work requirement.
        #
        # meets_ccdf_activity_test is a fallback input covering approved activities
        # we don't individually model, including the part-time-student-plus-40-
        # hours pathway (we don't track part-time school/training status here),
        # job search, education/training programs, SNAP E&T, and temporary leave.
        #
        # Not modeled (manual): the part-time-student + 40-hour pathway (use the
        # meets_ccdf_activity_test input); the "care based on the parent with the
        # least hours outside the home" nuance for mixed work/school two-parent
        # families; and the administrative checks (Work Verification Form,
        # 5-year degree-recency restriction, distance-learning accreditation).
        p = parameters(period).gov.states.mt.dphhs.ccap.eligibility.activity_hours
        person = spm_unit.members
        is_parent = person("is_tax_unit_head_or_spouse", period.this_year)
        monthly_hours = (
            person("weekly_hours_worked_before_lsr", period.this_year)
            * WEEKS_IN_YEAR
            / MONTHS_IN_YEAR
        )

        parent_count = spm_unit.sum(is_parent)
        two_parent = parent_count > 1

        # Parents whose work-hour obligation is waived. Incarceration only waives
        # within a two-parent family (the manual's "intact family" provision).
        is_waived_parent = is_parent & (
            person("is_full_time_student", period.this_year)
            | person("is_disabled", period.this_year)
            | (person("is_incarcerated", period) & spm_unit.project(two_parent))
        )
        working_parent = is_parent & ~is_waived_parent
        working_parent_count = spm_unit.sum(working_parent)
        working_parent_hours = spm_unit.sum(monthly_hours * working_parent)

        # Two parents still subject to the work requirement -> 120 combined hours;
        # otherwise the single-parent 60-hour standard applies to the remaining
        # (or lone) working parent.
        required_hours = where(working_parent_count >= 2, p.two_parent, p.single_parent)
        meets_hours = working_parent_hours >= required_hours
        all_parents_waived = (parent_count > 0) & (working_parent_count == 0)

        return (
            all_parents_waived
            | meets_hours
            | spm_unit("meets_ccdf_activity_test", period.this_year)
        )
