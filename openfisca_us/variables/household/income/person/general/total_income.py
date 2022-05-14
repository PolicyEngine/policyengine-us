from openfisca_us.model_api import *


class total_income(Variable):
    value_type = float
    entity = Person
    label = "Total income"
    unit = USD
    documentation = "Total of all income sources"
    definition_period = YEAR
