from policyengine_us.model_api import *


class dc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "DC TANF resources eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.dhs.tanf.resource_limit
        person = spm_unit.members
        # Check if the household has at least one elderly member.
        has_elderly = spm_unit.any(
            person("age", period) >= p.elderly_age_threshold
        )
        # Check if the household has at least one disabled member.
        has_disabled = spm_unit.any(person("is_disabled", period))
        # Look up resource limit by the condition.
        resource_limit = where(
            has_elderly | has_disabled,
            p.higher_limit,
            p.lower_limit,
        )
        countable_resources = spm_unit("dc_tanf_countable_resources", period)
        return countable_resources <= resource_limit
