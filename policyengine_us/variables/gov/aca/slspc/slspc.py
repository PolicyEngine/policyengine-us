from policyengine_us.model_api import *


class slspc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH

    adds = ["slspc_person"]
