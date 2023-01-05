from policyengine_us.model_api import *


class deep_poverty_gap(Variable):
    value_type = float
    entity = SPMUnit
    label = "deep poverty gap"
    unit = USD
    documentation = (
        "Difference between household income and deep poverty line."
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        deep_poverty_threshold = spm_unit("deep_poverty_line", period)
        return max_(deep_poverty_threshold - income, 0)
