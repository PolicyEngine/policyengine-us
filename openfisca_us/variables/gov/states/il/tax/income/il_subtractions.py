from openfisca_us.model_api import *


class il_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL subtractions"
    unit = USD
    definition_period = YEAR
    reference = ""
