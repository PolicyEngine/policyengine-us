from policyengine_us.model_api import *


class spm_unit_cash_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit cash assets"
    definition_period = YEAR
    unit = USD
