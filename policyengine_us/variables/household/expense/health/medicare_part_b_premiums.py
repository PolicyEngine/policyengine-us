from policyengine_us.model_api import *


class medicare_part_b_premiums(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit Medicare Part B premiums"
    definition_period = YEAR
    unit = USD
