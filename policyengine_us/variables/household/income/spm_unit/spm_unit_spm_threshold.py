from policyengine_us.model_api import *


class spm_unit_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's SPM poverty threshold"
    definition_period = YEAR
    unit = USD
