from policyengine_us.model_api import *


class nj_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Countable resources for New Jersey TANF"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
