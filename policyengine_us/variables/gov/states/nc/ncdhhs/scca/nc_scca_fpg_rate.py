from policyengine_us.model_api import *


class nc_scca_fpg_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program income limits compared to the FPL"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=8"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # Entry income eligibility depends on the child's age and disability status:
        # - Children aged 0-5 (preschool): 200% FPL
        # - Children aged 6-12 (school age): 133% FPL
        # - Children with special needs (any age): 200% FPL
        p = parameters(period).gov.states.nc.ncdhhs.scca

        # Retrieve age, school age status, and disability status for all members
        person = spm_unit.members
        is_school_age = person("nc_scca_is_school_age", period)
        disabled = person("is_disabled", period)

        # Check if any child is disabled and age-eligible for the program
        has_eligible_disabled_child = spm_unit.any(
            person("nc_scca_child_age_eligible", period) & disabled
        )

        # Check if all children are school age (if there are any children)
        has_any_children = spm_unit.any(person("is_child", period))
        all_children_school_age = ~has_any_children | (
            has_any_children
            & spm_unit.all(~person("is_child", period) | is_school_age)
        )

        # If there are any non-school age children or disabled children,
        # use the higher non-school age FPG limit, otherwise use school age limit
        has_preschool_or_special_needs = (
            has_eligible_disabled_child | ~all_children_school_age
        )

        # Select the appropriate FPG limit based on household composition
        # Children under school age (defined in p.age.school) or with special needs: 200% FPL
        # Only school-age children without special needs: 133% FPL
        return where(
            has_preschool_or_special_needs,
            p.entry.fpg_limit.preschool,
            p.entry.fpg_limit.school_age,
        )
