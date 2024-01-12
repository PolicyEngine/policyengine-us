from policyengine_us.model_api import *


class is_adopted(Variable):
    value_type = bool
    entity = Person
    label = "Is adopted"
    definition_period = YEAR
