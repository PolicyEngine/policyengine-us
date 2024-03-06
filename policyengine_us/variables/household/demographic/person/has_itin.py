from policyengine_us.model_api import *


class has_itin(Variable):
    value_type = bool
    entity = Person
    label = "Has ITIN or SSN"
    definition_period = YEAR
    default_value = True
