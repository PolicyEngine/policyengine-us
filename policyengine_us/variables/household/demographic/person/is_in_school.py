from policyengine_us.model_api import *


class is_in_school(Variable):
    value_type = bool
    entity = Person
    label = "Is in school"
    definition_period = YEAR
