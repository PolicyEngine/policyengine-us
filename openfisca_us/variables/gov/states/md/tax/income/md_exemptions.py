from openfisca_us.model_api import *


class md_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD exemptions"
    unit = USD
    definition_period = YEAR
