from openfisca_us.model_api import *


class fuel_cell_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified fuel cell property expenditures"
    documentation = "Expenditures for qualified fuel cell property installed on or in connection with a dwelling unit located in the United States and used as a principal residence by the taxpayer."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_3"
