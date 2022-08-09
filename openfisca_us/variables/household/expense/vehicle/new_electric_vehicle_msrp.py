from openfisca_us.model_api import *


class new_electric_vehicle_msrp(Variable):
    value_type = float
    entity = TaxUnit
    label = "New electric vehicle MSRP"
    documentation = "Manufacturer's suggested retail price of a newly purchased new electric vehicle"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
