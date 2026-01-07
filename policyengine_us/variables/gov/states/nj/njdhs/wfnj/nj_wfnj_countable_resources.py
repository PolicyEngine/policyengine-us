from policyengine_us.model_api import *


class nj_wfnj_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey WFNJ countable resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
