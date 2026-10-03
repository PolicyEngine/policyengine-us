from policyengine_us.model_api import *


class in_deep_poverty(Variable):
    value_type = float
    quantity_type = STOCK
    entity = SPMUnit
    label = "in deep poverty"
    documentation = "Whether a household is in deep poverty."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit("spm_unit_is_in_deep_spm_poverty", period)
