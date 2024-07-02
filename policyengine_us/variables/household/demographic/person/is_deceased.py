from policyengine_us.model_api import *


class is_deceased(Variable):
    value_type = bool
    entity = Person
    label = "Person is deceased"
    definition_period = YEAR
