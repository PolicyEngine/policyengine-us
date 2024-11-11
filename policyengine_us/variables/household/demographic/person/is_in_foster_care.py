from policyengine_us.model_api import *


class is_in_foster_care(Variable):
    value_type = bool
    entity = Person
    label = "Person is currently in a qualifying foster care institution"
    definition_period = MONTH
