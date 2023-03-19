from policyengine_us.model_api import *


class md_tanf_count_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "Maryland TANF number of children"
    definition_period = YEAR
    defined_for = StateCode.MD
    adds = "is_child"
