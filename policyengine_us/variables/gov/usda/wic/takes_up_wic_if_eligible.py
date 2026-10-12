from policyengine_us.model_api import *


class takes_up_wic_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person takes up WIC"
    definition_period = MONTH
    default_value = True
