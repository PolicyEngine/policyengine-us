from policyengine_us.model_api import *


class is_return_combined(Variable):
    value_type = bool
    entity = Person
    label = "Return Combined"
    documentation = "Whether the person's resident return is combined with another partner."
    definition_period = YEAR