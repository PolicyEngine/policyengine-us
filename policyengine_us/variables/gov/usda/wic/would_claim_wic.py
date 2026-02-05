from policyengine_us.model_api import *


class would_claim_wic(Variable):
    value_type = bool
    entity = Person
    label = "Would claim WIC"
    definition_period = MONTH

    def formula(person, period, parameters):
        draw = person("wic_takeup_draw", period)
        category = person("wic_category", period)
        takeup = parameters(period).gov.usda.wic.takeup
        return draw < takeup[category]
