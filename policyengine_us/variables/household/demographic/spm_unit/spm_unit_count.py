from policyengine_us.model_api import *


class spm_unit_count(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM units represented"
    definition_period = YEAR
    default_value = 1.0
