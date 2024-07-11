from policyengine_us.model_api import *


class is_(Variable):
    value_type = bool
    entity = Person
    label = "Is English Proficient"
    definition_period = YEAR
