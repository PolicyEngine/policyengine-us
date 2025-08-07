from policyengine_us.model_api import *


class is_chip_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CHIP eligible"
    definition_period = YEAR

    def formula(person, period, parameters):
        chip_category = person("chip_category", period)
        return chip_category != chip_category.possible_values.NONE
