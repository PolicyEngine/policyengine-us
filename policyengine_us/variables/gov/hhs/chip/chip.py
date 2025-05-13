from policyengine_us.model_api import *


class chip(Variable):
    value_type = float
    entity = Person
    label = "CHIP"
    unit = USD
    definition_period = YEAR
    reference = "https://www.macpac.gov/publication/chip-spending-by-state/"

    def formula(person, period, parameters):
        eligible = person("is_chip_eligible", period)
        benefit = person("per_capita_chip", period)
        return eligible * benefit
