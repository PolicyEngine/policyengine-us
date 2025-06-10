from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether a random eligible SPM unit does not claim ACA Premium Tax Credit"
    definition_period = YEAR
    default_value = True
