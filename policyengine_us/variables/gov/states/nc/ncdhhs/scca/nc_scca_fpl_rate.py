from policyengine_us.model_api import *


class nc_scca_fpl_rate(Variable):
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
        persons = spm_unit.members
        ages = persons("age", period)
        disabilities = persons("is_disabled", period)

        preschool_age_upper = p.preschool_age_upper
        disabled_age_limit = p.disabled_age_limit
        # get the youngest child's age
        min_age = min(ages)

        # Check if any child (6-17) is disabled
        has_disabled_child = spm_unit.any(
            (ages < disabled_age_limit) & disabilities
        )

        categorized_age = where(
            has_disabled_child | (min_age < preschool_age_upper),
            p.preschool_age_lower,
            p.preschool_age_upper,
        )

        return p.entry.income_rate_by_child_age.calc(categorized_age)
