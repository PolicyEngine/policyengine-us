from openfisca_us.model_api import *


class va_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA itemized deductions"
    unit = USD
    definition_period = YEAR

