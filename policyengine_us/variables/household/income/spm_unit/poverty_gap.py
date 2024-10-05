from policyengine_us.model_api import *


class poverty_gap(Variable):
    value_type = float
    entity = SPMUnit
    label = "poverty gap"
    unit = USD
    documentation = "Difference between household income and poverty line."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        poverty_threshold = spm_unit("spm_unit_spm_threshold", period)
        return max_(poverty_threshold - income, 0)
