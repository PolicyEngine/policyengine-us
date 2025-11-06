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
        # or child 6-11 when adequate child care is not available
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        is_parent = person("is_tax_unit_head_or_spouse", period)
        parent_count = person.spm_unit.sum(is_parent)

        # Check if there are children in the household under the age thresholds
        p = parameters(period).gov.usda.snap.student
        household_member_ages = person.spm_unit.members("age", period)
        has_young_child = person.spm_unit.any(
            household_member_ages < p.young_child
        )
        has_younger_child = person.spm_unit.any(
            household_member_ages < p.younger_child
        )

        # Two-parent households need child under 6
        # Single parent households need child under 12
        parent_exception_requirement = where(
            parent_count > 1, has_young_child, has_younger_child
        )

        return is_parent & parent_exception_requirement
