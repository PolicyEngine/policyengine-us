from policyengine_us.model_api import *


class aca_trimmed_age(Variable):
    value_type = int
    entity = Person
    label = "Age clipped to be in ACA last_same_child_age, max_adult_age range"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        aca = parameters(period).gov.aca
        return max_(aca.last_same_child_age, min_(aca.max_adult_age, age))
