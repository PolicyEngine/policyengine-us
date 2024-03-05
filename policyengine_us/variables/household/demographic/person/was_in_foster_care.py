from policyengine_us.model_api import *


class was_in_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Person was in the a qualifying foster care institution"
    definition_period = YEAR
