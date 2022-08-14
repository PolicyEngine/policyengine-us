from openfisca_us.model_api import *


class new_electric_vehicle_battery_components_made_in_north_america(Variable):
    value_type = float
    entity = TaxUnit
    label = "Percent of new electric vehicle's battery components made in North America"
    documentation = "Percent of newly purchased new electric vehicle's battery components (by value) manufactured or assembled in North America"
    unit = "/1"
    definition_period = YEAR
