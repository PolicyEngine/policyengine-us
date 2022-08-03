from openfisca_us.model_api import *


class mo_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO AGI subtractions"
    unit = USD
    definition_period = YEAR
    reference = ""
