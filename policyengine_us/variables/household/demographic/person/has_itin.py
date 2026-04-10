from policyengine_us.model_api import *


class has_itin(Variable):
    value_type = bool
    entity = Person
    label = "Deprecated alias for has_tin"
    definition_period = YEAR
    default_value = True

    def formula(person, period, parameters):
        return person("has_tin", period)
