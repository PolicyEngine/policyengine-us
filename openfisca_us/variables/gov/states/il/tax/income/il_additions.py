from openfisca_us.model_api import *

class il_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL additions"
    unit = USD
    definition_period = YEAR
    reference = ""