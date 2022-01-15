from openfisca_us.model_api import *


class market_income(Variable):
    value_type = float
    entity = Person
    label = "Market income"
    unit = USD
    documentation = "Income from all non-government sources"
    definition_period = YEAR
