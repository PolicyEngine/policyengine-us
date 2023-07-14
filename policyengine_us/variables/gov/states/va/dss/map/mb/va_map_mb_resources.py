from policyengine_us.model_api import *


class va_map_mb_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP MB QI countable resources"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        resources = person("va_map_resources", period) 
        mother = person("is_mother")
        father = person("is_father")
        c = mother | father
        
        return spm_unit.sum(resources) * c
