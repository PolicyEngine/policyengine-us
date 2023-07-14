from policyengine_us.model_api import *


class va_map_abd_resources_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD resources eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        resource = person("va_map_resources", period)
        mother = person("is_mother")
        father = person("is_father")
        c = mother | father
        resources = spm_unit.sum(resources) * c
        
        p = parameters(period).gov.states.va.dss.map.abd
        married = spm_unit("is_married", period)
        limit = where(married, p.resources_limit_couple, p.resources_limit_single)
        
        return resources <= limit
