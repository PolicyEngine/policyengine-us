from policyengine_us.model_api import *


class in_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = "in poverty"
    documentation = "Whether a household is in poverty."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit("poverty_gap", period) > 0
