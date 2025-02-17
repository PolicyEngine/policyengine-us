from policyengine_us.model_api import *


class is_newborn(Variable):
    value_type = bool
    entity = Person
    label = "Is a newborn child"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        return (age >= 0) & (age < 1)
