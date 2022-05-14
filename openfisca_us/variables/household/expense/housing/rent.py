from openfisca_us.model_api import *


class rent(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rent"
    unit = USD
    definition_period = YEAR
