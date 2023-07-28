from policyengine_us.model_api import *


class va_map_mb_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP MB countable resources"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        married = spm_unit("is_married", period)
        resources = person("va_map_resources", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        
        return spm_unit.sum(resources * where(married, head | spouse, head))
