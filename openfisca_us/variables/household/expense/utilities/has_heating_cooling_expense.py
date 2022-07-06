from openfisca_us.model_api import *


class has_heating_cooling_expense(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Has heating/cooling costs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, ["heating_cooling_expense"]) > 0
