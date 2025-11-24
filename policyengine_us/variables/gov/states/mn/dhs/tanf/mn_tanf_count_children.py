from policyengine_us.model_api import *


class mn_tanf_count_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "Minnesota MFIP number of children"
    definition_period = YEAR
    defined_for = StateCode.MN
    adds = ["is_child"]
