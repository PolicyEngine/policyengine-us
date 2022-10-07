from openfisca_us.model_api import *


class or_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
