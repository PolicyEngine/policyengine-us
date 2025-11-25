from policyengine_us.model_api import *


class meets_snap_parent_exception(Variable):
    value_type = bool
    entity = Person
    label = "Meets SNAP student parent exception"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#e_5, "
        "https://www.law.cornell.edu/uscode/text/7/2015#e_8"
    )

    def formula(person, period, parameters):
        # Exception 5: Parent with responsibility for dependent child under 6,
        # Or child 6-11 when adequate child care is not available (not modeled)
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        is_parent = person("is_tax_unit_head_or_spouse", period)
        spm_unit = person.spm_unit
        parent_count = spm_unit.sum(is_parent)

        # Check if there are children in the household under the age thresholds
        p = parameters(period).gov.usda.snap.student.child_age_limit
        household_member_ages = spm_unit.members("age", period)
        has_child_under_two_parent_limit = spm_unit.any(
            household_member_ages < p.two_parent
        )
        has_child_under_single_parent_limit = spm_unit.any(
            household_member_ages < p.single_parent
        )

        # Two-parent households need child under 6
        # Single parent households need child under 12, enrolled full-time
        is_full_time_student = person("is_full_time_college_student", period)
        parent_exception_requirement = where(
            parent_count > 1,
            has_child_under_two_parent_limit,
            has_child_under_single_parent_limit & is_full_time_student,
        )

        return is_parent & parent_exception_requirement
