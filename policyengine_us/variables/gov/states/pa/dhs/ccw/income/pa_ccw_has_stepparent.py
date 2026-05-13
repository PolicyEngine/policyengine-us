from policyengine_us.model_api import *


class pa_ccw_has_stepparent(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family includes a stepparent for Pennsylvania CCW"
    defined_for = StateCode.PA
