from policyengine_us.model_api import *


class would_claim_wic(Variable):
    value_type = bool
    entity = Person
    label = "Would claim WIC"
    definition_period = YEAR

    def formula(person, period, parameters):
        if person.count < 1_000:
            # Don't run takeup imputations if not in a microsimulation.
            return True
        category = person("wic_category", period)
        takeup = parameters(period).gov.usda.wic.takeup
        return random(person) < takeup[category]
