from policyengine_us.model_api import *


class is_male(Variable):
    value_type = bool
    entity = Person
    label = "is male"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        return ~person("is_female", period)
