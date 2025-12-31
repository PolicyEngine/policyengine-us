from policyengine_us.model_api import *


class sd_tanf_is_shared_living(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota TANF shared living arrangement"
    definition_period = MONTH
    default_value = False
    reference = (
        "https://www.law.cornell.edu/regulations/south-dakota/ARSD-67-10-05-03"
    )
    defined_for = StateCode.SD
