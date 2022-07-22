from openfisca_us.model_api import *


class tuition_and_fees(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tuition and fees (from Form 8917)"
    unit = USD
    definition_period = YEAR
