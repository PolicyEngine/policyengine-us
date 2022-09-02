from openfisca_us.model_api import *


class heat_pump_water_heater_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on heat pump water heaters"
    unit = USD
    definition_period = YEAR
    reference = (
        # Pre-IRA: Electric only.
        "https://www.law.cornell.edu/uscode/text/26/25C#d_3",
        # Post-IRA: Electric or natural gas.
        "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342",
    )
