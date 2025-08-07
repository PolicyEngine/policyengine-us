from policyengine_us.model_api import *


class is_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is a parent"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("own_children_in_household", period) > 0
