from policyengine_us.model_api import *


class snap_take_up_seed(Variable):
    value_type = float
    entity = SPMUnit
    label = "Randomly assigned seed for SNAP take-up"
    definition_period = YEAR
