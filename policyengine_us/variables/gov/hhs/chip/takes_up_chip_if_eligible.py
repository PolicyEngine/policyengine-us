from policyengine_us.model_api import *


class takes_up_chip_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person takes up CHIP"
    definition_period = YEAR
    default_value = True
