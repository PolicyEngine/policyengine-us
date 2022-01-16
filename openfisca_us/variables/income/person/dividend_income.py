from openfisca_us.model_api import *


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Dividend income"
    unit = USD
    documentation = "Dividend income"
    definition_period = YEAR
