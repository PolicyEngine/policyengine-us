from policyengine_us.model_api import *


class is_medicare_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for Medicare"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("age", period) >= 65
