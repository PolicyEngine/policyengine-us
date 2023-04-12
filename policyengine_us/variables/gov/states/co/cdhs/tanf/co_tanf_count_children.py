from policyengine_us.model_api import *


class co_tanf_count_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "Colorado TANF number of children"
    definition_period = YEAR
    defined_for = StateCode.CO
    adds = ["is_child", "is_pregnant"]
