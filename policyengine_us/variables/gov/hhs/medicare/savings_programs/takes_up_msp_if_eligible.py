from policyengine_us.model_api import *


class takes_up_msp_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person takes up the Medicare Savings Program"
    definition_period = YEAR
    default_value = True
