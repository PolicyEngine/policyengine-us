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
        # CC 2-3 Non-TANF Activity Requirements (CC23NonTANFActivity070718.pdf):
        # two-parent families need 120 activity hours/month total; single-parent
        # families need 60 work hours/month, or full-time school/training (no
        # work requirement), or part-time school plus 40 work hours/month.
        #
        # Unmodeled activity waivers / pathways (known modeling limitations):
        # - Part-time-student + 40-work-hours pathway (single- and two-parent):
        #   we don't currently track part-time vs full-time student status, so
        #   this pathway is collapsed into the full-time-student no-work-
        #   requirement path. This makes the model slightly more generous than
        #   the manual, which requires 40 work hours for a part-time student.
        # - Disabled-parent activity waiver: in a two-parent household with one
        #   disabled parent, the manual lets the other parent meet only the
        #   60-hr single-parent standard. We currently hold them to the 120-hr
        #   two-parent standard (slightly less generous). This is the most
        #   material candidate to model later; it would need a per-parent
        #   "unable to work due to disability" input.
        # - Incarcerated / pre-release parent: when one parent is incarcerated
        #   or in a pre-release program, the manual lets the other parent meet
        #   only the 60-hr single-parent standard. We don't currently model
        #   this (no per-parent incarceration/pre-release input).
        # - Teen-parent in-school waiver: a parent under 20 attending high
        #   school / HiSET has the work requirement waived. We don't currently
        #   model this.
        #
        # Administrative-verification items are intentionally not modeled: the
        # Work Verification Form, distance-learning program accreditation, and
        # the 5-year degree-recency restriction (per CC 2-3).
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
