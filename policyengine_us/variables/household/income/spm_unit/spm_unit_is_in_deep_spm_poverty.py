from policyengine_us.model_api import *
from policyengine_us.spm import nullable_spm_indicator, spm_universe_mask


class spm_unit_is_in_deep_spm_poverty(Variable):
    value_type = float
    quantity_type = STOCK
    entity = SPMUnit
    label = "SPM unit in deep SPM poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        spm_universe_mask(spm_unit, period)
        income = spm_unit("spm_unit_net_income", period)
        poverty_threshold = spm_unit("spm_unit_spm_threshold", period) / 2
        return nullable_spm_indicator(spm_unit, period, income, poverty_threshold)
