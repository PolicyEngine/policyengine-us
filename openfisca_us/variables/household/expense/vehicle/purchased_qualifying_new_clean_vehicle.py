from openfisca_us.model_api import *


class purchased_qualifying_new_clean_vehicle(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Purchased a qualifying new clean vehicle"
    definition_period = YEAR
