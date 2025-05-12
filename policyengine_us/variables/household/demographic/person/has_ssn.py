from policyengine_us.model_api import *


class has_ssn(Variable):
    value_type = bool
    entity = Person
    label = "Has SSN"
    definition_period = YEAR
    default_value = True
