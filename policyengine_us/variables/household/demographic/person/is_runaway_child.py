from policyengine_us.model_api import *


class is_runaway_child(Variable):
    value_type = bool
    entity = Person
    label = "Is runaway child"
    definition_period = YEAR
