from policyengine_us.model_api import *


class is_surviving_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Surviving Spouse"
    documentation = "Whether the person is a surviving spouse."
    definition_period = YEAR
