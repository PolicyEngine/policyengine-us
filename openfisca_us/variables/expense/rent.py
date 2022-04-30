from openfisca_us.model_api import *


class rent(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rent"
    documentation = "Rent"
    unit = USD
    definition_period = YEAR
