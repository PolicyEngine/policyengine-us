from openfisca_us.model_api import *


class geothermal_heat_pump_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified geothermal heat pump property expenditures"
    documentation = "Expenditures for qualified geothermal heat pump property installed on or in connection with a dwelling unit located in the United States and used as a residence by the taxpayer."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_5"
