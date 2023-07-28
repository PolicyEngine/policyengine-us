from policyengine_us.model_api import *


class va_map_abd_resources_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD resources eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        resources = spm_unit("va_map_abd_resources", period)
        limit = spm_unit("va_map_abd_resources_limit", period)
        return resources <= limit
