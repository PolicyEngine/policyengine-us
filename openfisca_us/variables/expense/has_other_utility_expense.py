from openfisca_us.model_api import *


class has_other_utility_expense(Variable):
    value_type = bool
    entity = Household
    label = "Has other utility expenses"
    documentation = "Whether the household has utility bills other than heating/cooling and telephone"
    definition_period = YEAR
