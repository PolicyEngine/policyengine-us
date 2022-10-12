from policyengine_us.model_api import *


class new_clean_vehicle_msrp(Variable):
    value_type = float
    entity = TaxUnit
    label = "New clean vehicle MSRP"
    documentation = "Manufacturer's suggested retail price of a newly purchased new clean vehicle"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
