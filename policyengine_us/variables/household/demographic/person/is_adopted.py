from policyengine_us.model_api import *


class is_adopted(Variable):
    value_type = bool
    entity = Person
    label = "Is adopted"
    definition_period = YEAR

    def formula(person, period, parameters):
        is_adopted = person("adopted_this_year", period)
        node = period.last_year
        while node:
            is_adopted = is_adopted | person("adopted_this_year", node)
            node = node.last_year
        return is_adopted
