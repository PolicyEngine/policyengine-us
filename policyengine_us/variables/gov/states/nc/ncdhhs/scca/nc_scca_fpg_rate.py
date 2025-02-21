from policyengine_us.model_api import *


class nc_scca_fpg_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program income limits compared to the FPL"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=8"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # entry income eligible depends on the youngest child's age,
        # 0-5, or with specail needs, 200% fpl
        # 6-12, 133%
        p = parameters(period).gov.states.nc.ncdhhs.scca

        # Retrieve age and disability status for all members
        person = spm_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)

        # get the youngest child's age
        min_age = spm_unit.min(age)

        # Check if any child (6-17) is disabled
        has_disabled_child = spm_unit.any(
            (age < p.age_limit.disabled_age_limit) & disabled
        )

        categorized_age = where(
            has_disabled_child
            | (min_age < p.age_limit.three_to_five_year_olds_age_upper),
            p.age_limit.three_to_five_year_olds_age_lower,
            p.age_limit.three_to_five_year_olds_age_upper,
        )

        return p.entry.income_rate_by_child_age.calc(categorized_age)
