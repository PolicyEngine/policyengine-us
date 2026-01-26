from policyengine_us.model_api import *


class ny_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF resources eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/tanf/TANF-State-Plan-2021-2023.pdf#page=7"
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.ny.otda.tanf.resources
        person_meets_higher_limit_age = (
            person("age", period.this_year)
            >= p.higher_resource_limit_age_threshold
        )
        has_anyone_with_higher_limit_age = spm_unit.any(
            person_meets_higher_limit_age
        )
        resource_limit = where(
            has_anyone_with_higher_limit_age,
            p.higher_limit,
            p.lower_limit,
        )
        countable_resources = spm_unit("ny_tanf_countable_resources", period)
        return countable_resources <= resource_limit
