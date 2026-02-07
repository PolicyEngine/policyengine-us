from policyengine_us.model_api import *


class takes_up_ssi_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Takes up SSI if eligible"
    definition_period = YEAR
    default_value = True
