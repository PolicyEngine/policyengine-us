from policyengine_us.model_api import *


class spm_unit_count_children(Variable):
    value_type = int
    entity = SPMUnit
    label = "children in SPM unit"
    definition_period = YEAR
    adds = ["is_child"]
