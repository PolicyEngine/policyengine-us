from policyengine_us.model_api import *


class is_stillbirth(Variable):
    value_type = bool
    entity = Person
    label = "Is a stillbirth child"
    definition_period = YEAR