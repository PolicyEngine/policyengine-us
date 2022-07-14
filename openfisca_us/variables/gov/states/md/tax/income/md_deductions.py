from openfisca_us.model_api import *


class md_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deductions"
    unit = USD
    definition_period = YEAR
