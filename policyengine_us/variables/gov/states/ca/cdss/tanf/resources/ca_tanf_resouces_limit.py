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
        has_elderly = spm_unit.any(person("age", period) >= p.age_threshold)
        has_disabled = spm_unit.any(person("is_disabled", period))
        return where(has_elderly | has_disabled, p.higher, p.lower)
