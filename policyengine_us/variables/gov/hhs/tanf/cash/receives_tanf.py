from policyengine_us.model_api import *


class receives_tanf(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Reported to receive TANF"
    definition_period = MONTH
