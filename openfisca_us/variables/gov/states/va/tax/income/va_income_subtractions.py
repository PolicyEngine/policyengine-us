from openfisca_us.model_api import *


class va_income_substractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA income substractions from schedule ADJ"
    unit = USD
    definition_period = YEAR
