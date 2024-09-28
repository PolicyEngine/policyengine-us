from policyengine_us.model_api import *


class takes_up_snap_if_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether a random eligible SPM unit does not claim SNAP"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        return random(spm_unit) < parameters(period).gov.usda.snap.takeup_rate
