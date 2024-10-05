from policyengine_us.model_api import *


class in_deep_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = "in deep poverty"
    documentation = "Whether a household is in deep poverty."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit("deep_poverty_gap", period) > 0
