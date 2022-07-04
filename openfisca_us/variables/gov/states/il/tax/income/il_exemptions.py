from openfisca_us.model_api import *

class il_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL exemptions"
    unit = USD
    definition_period = YEAR
    reference = ""