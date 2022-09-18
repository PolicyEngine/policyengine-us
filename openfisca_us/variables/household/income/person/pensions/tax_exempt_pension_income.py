from openfisca_us.model_api import *


class tax_exempt_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt pension income"
    unit = USD
    definition_period = YEAR
