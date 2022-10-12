from policyengine_us.model_api import *


class is_child(Variable):
    value_type = bool
    entity = Person
    label = "Is a child"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) < 18
