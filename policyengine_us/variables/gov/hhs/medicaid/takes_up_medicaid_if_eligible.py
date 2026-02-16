from policyengine_us.model_api import *


class takes_up_medicaid_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person takes up Medicaid"
    definition_period = YEAR
    default_value = True
