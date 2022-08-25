from openfisca_us.model_api import *


class insulation_air_sealing_and_ventilation_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on insulation, air sealing, and ventilation"
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585"
