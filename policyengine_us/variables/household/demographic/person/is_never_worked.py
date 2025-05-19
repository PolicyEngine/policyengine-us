from policyengine_us.model_api import *


class is_never_worked(Variable):
    value_type = bool
    entity = Person
    label = "Has never worked"
    definition_period = YEAR
