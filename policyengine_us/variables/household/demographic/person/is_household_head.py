from policyengine_us.model_api import *


class is_household_head(Variable):
    value_type = bool
    entity = Person
    label = "is head of this household"
    definition_period = ETERNITY
