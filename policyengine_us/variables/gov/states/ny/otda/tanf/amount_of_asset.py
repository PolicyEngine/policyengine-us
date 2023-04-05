from policyengine_us.model_api import *


class amount_of_asset(Variable):
    value_type = float
    entity = SPMUnit
    label = "Amount of asset"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
