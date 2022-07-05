from openfisca_us.model_api import *


class va_low_income_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax credit for low-income individuals or Virginia EITC"
    unit = USD
    definition_period = YEAR
