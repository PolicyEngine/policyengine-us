from policyengine_us.model_api import *


class is_in_secondary_school(Variable):
    value_type = bool
    entity = Person
    label = "Is in secondary school (or in an equivalent level of training)"
    definition_period = YEAR
