from policyengine_us.model_api import *


class ny_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Countable resources for New York TANF"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
