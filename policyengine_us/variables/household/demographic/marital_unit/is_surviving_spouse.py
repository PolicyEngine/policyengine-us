from policyengine_us.model_api import *


class is_surviving_spouse(Variable):
    value_type = bool
    entity = Person
    label = "surviving spouse"
    documentation = "Whether the person is surviving spouse."
    definition_period = YEAR
