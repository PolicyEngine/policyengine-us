from policyengine_us.model_api import *


class deep_poverty_line(Variable):
    value_type = float
    entity = SPMUnit
    label = "deep poverty line"
    unit = USD
    documentation = "Income threshold below which a household is considered to be in deep poverty."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit("poverty_line", period) / 2
