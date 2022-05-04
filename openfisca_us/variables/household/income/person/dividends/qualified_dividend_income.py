from openfisca_us.model_api import *


class qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified dividend income"
    unit = USD
    definition_period = YEAR
