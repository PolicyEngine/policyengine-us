from openfisca_us.model_api import *


class natural_gas_heat_pump_water_heater_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Natural gas heat pump water heater expenditures"
    documentation = (
        "Expenditures on qualified natural gas heat pump water heaters"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#d_3"
    reference
