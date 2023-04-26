from policyengine_us.model_api import *


class md_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maryland TANF eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
