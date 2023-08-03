from policyengine_us.model_api import *


class ny_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF resources eligible"
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        # The amount of assets that a family may own and qualify for FA is $2,000
        # except for households in which any member is age 60 or over in which case $3,000 in assets can be owned.
        # https://otda.ny.gov/policy/tanf/TANF-State-Plan-2021-2023.pdf#page=7, #10
        person = spm_unit.members
        p = parameters(period).gov.states.ny.otda.tanf.eligibility.resources
        person_meets_higher_resource_limit_age = (
            person("age", period) >= p.higher_resource_limit_age_threshold
        )
        has_anyone_with_higher_resource_limit_age = spm_unit.any(
            person_meets_higher_resource_limit_age
        )
        resource_limit = where(
            has_anyone_with_higher_resource_limit_age,
            p.higher_limit,
            p.lower_limit,
        )
        countable_resources = spm_unit("ny_tanf_countable_resources", period)
        return countable_resources <= resource_limit
