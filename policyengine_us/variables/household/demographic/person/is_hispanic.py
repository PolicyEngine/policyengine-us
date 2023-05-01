from policyengine_us.model_api import *


class is_hispanic(Variable):
    value_type = bool
    entity = Person
    label = "hispanic"
    documentation = "Whether the person is Hispanic"
    definition_period = YEAR
