from policyengine_us.model_api import *


class was_teen_parent_at_first_birth(Variable):
    value_type = bool
    entity = Person
    label = "Was a teen parent at birth of first child"
    definition_period = YEAR
    documentation = "Whether the parent was a teenager (under 20) when their first child was born"
