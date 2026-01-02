from policyengine_us.model_api import *


class wy_tanf_shelter_qualified(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wyoming TANF shelter qualified"
    definition_period = MONTH
    reference = "https://dfs.wyo.gov/about/policy-manuals/snap-and-power-policy-manual/"
    defined_for = StateCode.WY
    default_value = True
