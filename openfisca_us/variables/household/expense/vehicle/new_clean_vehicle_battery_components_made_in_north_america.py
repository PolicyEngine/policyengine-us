from openfisca_us.model_api import *


class new_clean_vehicle_battery_components_made_in_north_america(Variable):
    value_type = float
    entity = TaxUnit
    label = "Percent of new clean vehicle's battery components made in North America"
    documentation = "Percent of newly purchased new clean vehicle's battery components (by value) manufactured or assembled in North America"
    unit = "/1"
    definition_period = YEAR
