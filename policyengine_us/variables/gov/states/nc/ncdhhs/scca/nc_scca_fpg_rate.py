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

        # Retrieve age and disability status for all members
        person = spm_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)

        # Get the youngest child's age
        min_age = spm_unit.min(age)

        # Check if any child is disabled
        has_disabled_child = spm_unit.any(
            (age < p.age.limit.disabled) & disabled
        )

        # Determine if the household has a non-school age child (under 6) or special needs child
        school_age_threshold = p.age.school_age
        has_preschool_or_special_needs = has_disabled_child | (
            min_age < school_age_threshold
        )

        # Select the appropriate FPG limit based on household composition
        return where(
            has_preschool_or_special_needs,
            p.entry.fpg_limit_by_school_age.non_school_age,
            p.entry.fpg_limit_by_school_age.school_age,
        )
