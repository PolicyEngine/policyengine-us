from policyengine_us.model_api import *


class has_special_needs(Variable):
    value_type = bool
    entity = Person
    label = "Has special needs"
    definition_period = YEAR
