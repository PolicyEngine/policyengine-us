from policyengine_us.model_api import *


class wic_takeup_draw(Variable):
    value_type = float
    entity = Person
    label = "Random draw for WIC take-up"
    definition_period = MONTH

    def formula(person, period, parameters):
        if person.simulation.dataset is not None:
            return random(person)
        return 0
