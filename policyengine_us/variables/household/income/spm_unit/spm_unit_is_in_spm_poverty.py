from policyengine_us.model_api import *
from policyengine_us.spm import nullable_spm_indicator


class spm_unit_is_in_spm_poverty(Variable):
    value_type = float
    quantity_type = STOCK
    entity = SPMUnit
    label = "SPM unit in SPM poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        poverty_threshold = spm_unit("spm_unit_spm_threshold", period)
        return nullable_spm_indicator(spm_unit, period, income, poverty_threshold)
