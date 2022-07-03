from openfisca_us.model_api import *


class va_spouse_tax_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia spouse tax adjustment"
    unit = USD
    definition_period = YEAR
