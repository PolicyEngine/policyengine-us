from policyengine_us.model_api import *


class is_union_member_or_covered(Variable):
    value_type = bool
    entity = Person
    label = "is union member or covered by a union contract"
    definition_period = YEAR
