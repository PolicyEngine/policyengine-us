from policyengine_us.model_api import *


class is_separated(Variable):
    value_type = bool
    entity = Person
    label = "Separated"
    documentation = "Whether the person is separated from a partner."
    definition_period = YEAR
