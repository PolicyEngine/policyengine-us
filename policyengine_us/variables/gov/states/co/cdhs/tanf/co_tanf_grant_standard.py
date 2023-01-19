from policyengine_us.model_api import *


class co_tanf_grant_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "CO TANF grant standard"
    unit = USD
    definition_period = YEAR
    defined_for = "co_tanf_eligible"
