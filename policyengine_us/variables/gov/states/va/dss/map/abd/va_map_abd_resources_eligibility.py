from policyengine_us.model_api import *


class va_map_abd_resources_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD resources eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        resources = add(spm_unit, period, 'va_map_countable_resources')
        p = parameters(period).gov.states.va.dss.map.abd
        person = spm_unit.members
        married = person("is_married", period)
        limit = p.resources_limit_single
        if spm_unit.any(married):
            limit = p.resources_limit_couple

        return resources <= limit
