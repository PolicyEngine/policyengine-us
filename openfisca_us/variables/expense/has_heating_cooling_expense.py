from openfisca_us.model_api import *


class has_heating_cooling_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has heating/cooling costs"
    documentation = "Whether the household has heating/cooling costs"
    definition_period = YEAR
