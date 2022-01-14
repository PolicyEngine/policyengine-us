from openfisca_us.model_api import *


class spm_unit_ccdf_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SPM unit CCDF subsidy"
    unit = USD

    def formula(spm_unit, period, parameters):
        total_market_rate = spm_unit(
            "spm_unit_total_childcare_market_rate", period
        )
        total_copay = spm_unit("spm_unit_total_ccdf_copay", period)
        return total_market_rate - total_copay
