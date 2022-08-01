from openfisca_us.model_api import *


class new_electric_vehicle_battery_percent_made_in_north_america(Variable):
    value_type = float
    entity = TaxUnit
    label = "Percent of new electric vehicle's battery made in North America"
    label = "Percent of newly purchased new electric vehicle's battery's value manufactured or assembled in North America"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=372"
