from policyengine_us.model_api import *


class own_children_in_household(Variable):
    value_type = int
    entity = Person
    label = "Count of one's own children in the household"
    definition_period = YEAR
