from openfisca_us.model_api import *


class biomass_stove_boiler_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Biomass stoves and boilers expenditures"
    documentation = "Expenditures on biomass stoves and boilers"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#d_4"
