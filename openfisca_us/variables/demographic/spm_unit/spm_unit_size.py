from openfisca_us.model_api import *


class spm_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SPM unit size"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return spm_unit.nb_persons()
