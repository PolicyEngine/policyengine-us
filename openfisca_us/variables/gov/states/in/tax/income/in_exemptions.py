from openfisca_us.model_api import *


class in_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN exemptions"
    unit = USD
    definition_period = YEAR
