from policyengine_us.model_api import *


class mn_mfip_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    adds = ["spm_unit_assets"]
