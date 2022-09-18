from openfisca_us.model_api import *


class biomass_stove_boiler_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on biomass stoves and boilers"
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342"
