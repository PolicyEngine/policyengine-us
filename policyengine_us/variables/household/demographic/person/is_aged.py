from policyengine_us.model_api import *


class is_aged(Variable):
    value_type = bool
    entity = Person
    label = "Is over 65 years old"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) >= 65
