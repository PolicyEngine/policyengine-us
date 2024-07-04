from policyengine_us.model_api import *


class is_migrant_child(Variable):
    value_type = bool
    entity = Person
    label = "Is migrant child"
    definition_period = YEAR
