from policyengine_us.model_api import *


class aca_slspc_trimmed_age(Variable):
    value_type = int
    entity = Person
    label = (
        "Age clipped to be in ACA SLSPC "
        "last_same_child_age, max_adult_age range"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.aca.slspc
        return max_(p.last_same_child_age, min_(p.max_adult_age, age))
