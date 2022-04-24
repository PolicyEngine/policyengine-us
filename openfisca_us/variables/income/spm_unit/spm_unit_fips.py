from openfisca_us.model_api import *


class spm_unit_fips(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit FIPS code"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit.household("fips", period)
