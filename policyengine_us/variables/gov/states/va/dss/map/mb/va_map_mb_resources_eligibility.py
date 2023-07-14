from policyengine_us.model_api import *


class va_map_mb_resources_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP MB resources eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        resources = spm_unit("va_map_mb_resources", period)
        p = parameters(period).gov.states.va.dss.map.mb
        married = spm_unit("is_married", period)
        if married:
            p = p.resources_limit_couple
        else:
            p = p.resources_limit_single
        return resources <= p