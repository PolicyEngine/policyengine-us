from policyengine_us.model_api import *


class spm_unit_count_adults(Variable):
    value_type = int
    entity = SPMUnit
    label = "adults in SPM unit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("is_adult", period))
