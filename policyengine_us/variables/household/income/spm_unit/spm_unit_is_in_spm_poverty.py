from policyengine_us.model_api import *


class spm_unit_is_in_spm_poverty(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM unit in SPM poverty"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        poverty_threshold = spm_unit("spm_unit_spm_threshold", period)
        return income < poverty_threshold
