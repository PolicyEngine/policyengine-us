from openfisca_us.model_api import *


class va_income_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA income additions"
    unit = USD
    definition_period = YEAR
