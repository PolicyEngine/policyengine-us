from policyengine_us.model_api import *


class va_map_abd_resources_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP ABD resources limit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.abd
        married = spm_unit("is_married", period)
        return where(married, p.resources_limit_couple, p.resources_limit_single)