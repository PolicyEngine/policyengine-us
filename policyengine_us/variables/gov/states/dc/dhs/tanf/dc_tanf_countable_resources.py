from policyengine_us.model_api import *


class dc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
