from openfisca_us.model_api import *


class advanced_main_air_circulating_fan_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on advanced main air circulating fans"
    documentation = "Must be used in a natural gas, propane, or oil furnaces and which have an annual electricity use of no more than 2 percent of the total annual energy use of the furnace."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#d_5"
