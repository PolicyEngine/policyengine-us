from policyengine_us.model_api import *


class snap_utility_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Standard Utility Allowance"
    unit = USD
    documentation = "The regular utility allowance deduction for SNAP"
    definition_period = MONTH

    adds = [
        "snap_standard_utility_allowance",
        "snap_limited_utility_allowance",
        "snap_individual_utility_allowance",
    ]
