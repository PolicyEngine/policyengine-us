from openfisca_us.model_api import *


class household_vehicles_owned(Variable):
    value_type = float
    entity = Household
    label = "Vehicles owned"
    unit = USD
    definition_period = YEAR
