from openfisca_us.model_api import *


class would_claim_wic(Variable):
    value_type = bool
    entity = Person
    label = "Would claim WIC"
    definition_period = YEAR

    def formula(person, period, parameters):
        category = person("wic_category", period)
        takeup = parameters(period).usda.wic.takeup
        return random(person) < takeup[category]
