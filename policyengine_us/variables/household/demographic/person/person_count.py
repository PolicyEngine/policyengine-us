from policyengine_us.model_api import *


class person_count(Variable):
    value_type = float
    entity = Person
    label = "People represented"
    definition_period = YEAR
    default_value = 1.0
