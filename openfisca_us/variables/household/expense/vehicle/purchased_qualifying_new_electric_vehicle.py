from openfisca_us.model_api import *


class purchased_qualifying_new_electric_vehicle(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Purchased a qualifying new electric vehicle"
    definition_period = YEAR
