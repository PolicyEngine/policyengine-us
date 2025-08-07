from policyengine_us.model_api import *


class is_military(Variable):
    value_type = bool
    entity = Person
    label = "is employed in the US armed forces"
    definition_period = YEAR
