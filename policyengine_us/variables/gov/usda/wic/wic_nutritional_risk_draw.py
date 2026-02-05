from policyengine_us.model_api import *


class wic_nutritional_risk_draw(Variable):
    value_type = float
    entity = Person
    label = "Random draw for WIC nutritional risk"
    definition_period = MONTH

    def formula(person, period, parameters):
        if person.simulation.dataset is not None:
            return random(person)
        return 0
