from policyengine_us.model_api import *


class would_claim_wic(Variable):
    value_type = bool
    entity = Person
    label = "Would claim WIC"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Assign households WIC takeup probabilistically in microsimulation.
        # Assume all take up in individual simulation.
        if person.simulation.dataset is not None:
            category = person("wic_category", period)
            takeup = parameters(period).gov.usda.wic.takeup
            return random(person) < takeup[category]
        else:
            return True
