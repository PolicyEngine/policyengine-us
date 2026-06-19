from policyengine_us.model_api import *


class receives_snap(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Reported to receive SNAP"
    definition_period = MONTH
