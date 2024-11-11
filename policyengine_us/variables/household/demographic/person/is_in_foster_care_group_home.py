from policyengine_us.model_api import *


class is_in_foster_care_group_home(Variable):
    value_type = bool
    entity = Person
    label = "Person is currently in a qualifying foster care group home"
    definition_period = MONTH
    default_value = False
    defined_for = "is_in_foster_care"
