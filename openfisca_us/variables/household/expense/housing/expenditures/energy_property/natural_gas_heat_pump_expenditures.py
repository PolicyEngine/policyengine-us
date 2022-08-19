from openfisca_us.model_api import *


class natural_gas_heat_pump_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Natural gas heat pump expenditures"
    documentation = "Expenditures on qualified natural gas heat pumps"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.law.cornell.edu/uscode/text/26/25C#d_3" ,
    "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342" ,
 