from policyengine_us.model_api import *


class is_enrolled_in_ccdf(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "CCDF enrollment status"
