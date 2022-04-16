from openfisca_us.model_api import *


class household_vehicles_owned(Variable):
    value_type = float
    entity = Household
    label = "Vehicles owned"
    unit = USD
    documentation = "Number of vehicles owned by the household"
    definition_period = YEAR
