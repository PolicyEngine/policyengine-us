from policyengine_us.model_api import *


class is_adult(Variable):
    value_type = bool
    entity = Person
    label = "Is an adult"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) >= 18
