from policyengine_us.model_api import *


class co_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "CO TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.CO
