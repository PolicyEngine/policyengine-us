from policyengine_us.model_api import *


class snap_takeup_draw(Variable):
    value_type = float
    entity = SPMUnit
    label = "Random draw for SNAP take-up"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        if spm_unit.simulation.dataset is not None:
            return random(spm_unit)
        return 0
