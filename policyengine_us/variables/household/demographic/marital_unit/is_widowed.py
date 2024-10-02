from policyengine_us.model_api import *


class is_widowed(Variable):
    value_type = bool
    entity = Person
    label = "Widowed"
    documentation = "Whether the person is widowed."
    definition_period = YEAR
