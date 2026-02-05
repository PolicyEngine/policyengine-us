from policyengine_us.model_api import *


class ssi_resource_test_draw(Variable):
    value_type = float
    entity = Person
    label = "Random draw for SSI resource test"
    definition_period = YEAR

    def formula(person, period, parameters):
        if person.simulation.dataset is not None:
            return random(person)
        return 0
