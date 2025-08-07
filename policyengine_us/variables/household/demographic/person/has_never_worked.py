from policyengine_us.model_api import *


class has_never_worked(Variable):
    value_type = bool
    entity = Person
    label = "has never worked"
    definition_period = YEAR
