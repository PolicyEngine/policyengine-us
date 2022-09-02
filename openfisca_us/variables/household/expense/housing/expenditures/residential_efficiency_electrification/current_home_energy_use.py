from openfisca_us.model_api import *


class current_home_energy_use(Variable):
    value_type = float
    entity = Household
    label = "Current home energy use in monthly kilowatt hours"
    unit = "kWh/month"
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587"
