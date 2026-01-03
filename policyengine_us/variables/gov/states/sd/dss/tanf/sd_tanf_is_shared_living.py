from policyengine_us.model_api import *


class sd_tanf_is_shared_living(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota TANF shared living arrangement"
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:05:03"
    defined_for = StateCode.SD
