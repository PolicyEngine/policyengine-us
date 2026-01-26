from policyengine_us.model_api import *


class ny_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York TANF resources eligible"
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://otda.ny.gov/policy/directives/2022/ADM/22-ADM-11.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.ny.otda.tanf

        # Age 60+ always qualifies for higher limit
        person_meets_age_threshold = (
            person("age", period.this_year)
            >= p.resource_limit.higher.age_threshold
        )
        has_elderly_member = spm_unit.any(person_meets_age_threshold)

        # Disability qualifier added by October 2022 reform
        person_is_disabled = person("is_disabled", period)
        has_disabled_member = spm_unit.any(person_is_disabled)

        qualifies_for_higher_limit = where(
            p.reform_2022.in_effect,
            has_elderly_member | has_disabled_member,
            has_elderly_member,
        )

        resource_limit = where(
            qualifies_for_higher_limit,
            p.resource_limit.higher.amount,
            p.resource_limit.lower.amount,
        )
        resources = spm_unit("spm_unit_assets", period.this_year)
        return resources <= resource_limit
