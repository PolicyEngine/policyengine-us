from openfisca_us.model_api import *


class dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Dividend income"
    unit = USD
    definition_period = YEAR
