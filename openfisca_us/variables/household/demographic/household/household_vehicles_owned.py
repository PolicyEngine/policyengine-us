from openfisca_us.model_api import *


class household_vehicles_owned(Variable):
    value_type = int
    entity = Household
    label = "Vehicles owned"
    definition_period = YEAR
