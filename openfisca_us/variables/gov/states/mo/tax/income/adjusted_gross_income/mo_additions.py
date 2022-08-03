from openfisca_us.model_api import *


class mo_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO AGI additions"
    unit = USD
    definition_period = YEAR
    reference = ""
