from policyengine_us.model_api import *


class ca_tanf_resouces_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Resources Limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.resources.limit
        person = spm_unit.members
        age = person("age", period)
        has_elderly = spm_unit.any(age >= p.age_threshold)
        is_disabled = person("is_disabled", period)
        has_disabled_member = spm_unit.any(is_disabled)
        return where(has_elderly | has_disabled_member, p.with_elderly_or_disabled_member.yaml, p.without_elderly_or_disabled_member.yaml)
