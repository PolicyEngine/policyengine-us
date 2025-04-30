from policyengine_us.model_api import *


class dc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "DC Temporary Assistance for Needy Families (TANF) countable resources"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.DC
