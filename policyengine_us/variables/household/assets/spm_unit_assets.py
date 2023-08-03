from policyengine_us.model_api import *


class spm_unit_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit assets"
    definition_period = YEAR
    unit = USD
