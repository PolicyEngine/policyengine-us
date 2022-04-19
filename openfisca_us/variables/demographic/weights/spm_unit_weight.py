from openfisca_us.model_api import *


class spm_unit_weight(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit weight"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Use household weights if not provided
        return spm_unit.household("household_weight", period)
