from openfisca_us.model_api import *


class va_adj_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA deductions from schedule ADJ"
    unit = USD
    definition_period = YEAR

