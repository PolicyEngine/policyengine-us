from openfisca_us.model_api import *


class retrofit(Variable):
    value_type = float
    entity = Household
    label = "Achieved modeled energy system savings"
    definition_period = YEAR
