from openfisca_us.model_api import *


class purchased_qualifying_used_electric_vehicle(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Purchased a qualifying used electric vehicle"
    definition_period = YEAR
