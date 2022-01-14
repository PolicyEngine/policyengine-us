from openfisca_us.model_api import *


class spm_unit_total_childcare_market_rate(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SPM unit total childcare market rate"
    unit = USD

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("ccdf_market_rate", period))
