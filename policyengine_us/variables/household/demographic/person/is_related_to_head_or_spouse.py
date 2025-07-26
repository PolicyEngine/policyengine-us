from policyengine_us.model_api import *


class is_related_to_head_or_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Person is related to head or spouse"
    definition_period = YEAR
    default_value = True
