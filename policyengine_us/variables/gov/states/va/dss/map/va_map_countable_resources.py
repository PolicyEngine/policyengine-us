from policyengine_us.model_api import *


class va_map_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
