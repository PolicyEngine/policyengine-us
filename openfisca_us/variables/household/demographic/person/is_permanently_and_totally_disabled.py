from policyengine_us.model_api import *


class is_permanently_and_totally_disabled(Variable):
    value_type = bool
    entity = Person
    label = "Is permanently and totally disabled"
    definition_period = YEAR
