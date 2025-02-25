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

        # Determine the threshold age for FPG limit calculation
        # If there's a disabled child or any non-school age child, use age 0 (200% FPL)
        # Otherwise use age 6 (133% FPL)
        threshold_age = where(
            has_preschool_or_special_needs,
            0,  # Use the 0-5 threshold (200% FPL)
            6,  # Use the 6+ threshold (133% FPL)
        )
        
        # Use calc method with the bracket parameter structure
        return p.entry.fpg_limit_by_school_age.calc(threshold_age)
