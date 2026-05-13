from policyengine_us.model_api import *


class takes_up_basic_health_program_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person takes up Basic Health Program coverage"
    definition_period = YEAR
    default_value = True
