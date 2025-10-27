from policyengine_us.model_api import *


class is_snap_ineligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Is an ineligible student for SNAP"
    documentation = (
        "Whether this person is ineligible for SNAP due to student status. "
        "Under 7 USC 2015(e), individuals enrolled at least half-time in "
        "higher education are generally ineligible, unless they meet one of "
        "eight statutory exceptions."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2015#e"

    def formula(person, period, parameters):
        # Base rule: Students enrolled at least half-time in higher education
        # are ineligible (K-12 students are not affected by this rule)
        # Note: Currently we only check full-time college students, but the
        # statute covers half-time or more
        is_higher_ed_student = person("is_full_time_college_student", period)

        # Eight statutory exceptions that make students eligible:

        # Exception 1: Under 18 or age 50 or older
        age = person("age", period)
        p = parameters(period).gov.usda.snap.student
        meets_age_exception = p.age_threshold.calc(age)

        # Exception 2: Not physically or mentally fit (disabled)
        meets_disability_exception = person("is_disabled", period)

        # Exception 3: Employment/training programs (WIOA, career/technical ed)

        # Exception 4: Employed at least 20 hours per week or work-study
        hours_worked = person("weekly_hours_worked", period)
        meets_work_hours_exception = hours_worked >= p.working_hours_threshold

        # Exception 5: Parent caring for dependent child under 6.
        # Exception 8: Single parent with responsibility for dependent under 12
        is_parent = person("is_tax_unit_head_or_spouse", period)
        parent_count = person.spm_unit.sum(is_parent)

        # Check if there are children in the household under the age thresholds
        household_member_ages = person.spm_unit.members("age", period)
        has_young_child = person.spm_unit.any(
            household_member_ages < p.young_child
        )
        has_younger_child = person.spm_unit.any(
            household_member_ages < p.younger_child
        )

        parent_exception_requirement = where(
            parent_count > 1, has_young_child, has_younger_child
        )
        meets_parent_exception = is_parent & parent_exception_requirement

        # Exception 6: Receiving TANF benefits
        tanf = person("tanf_person", period)
        receives_tanf = tanf > 0

        # Student is INELIGIBLE if they are a higher ed student AND
        # they do NOT meet ANY of the eight exceptions
        meets_any_exception = (
            meets_age_exception
            | meets_disability_exception
            | meets_work_hours_exception
            | meets_parent_exception
            | receives_tanf
        )

        return is_higher_ed_student & ~meets_any_exception
