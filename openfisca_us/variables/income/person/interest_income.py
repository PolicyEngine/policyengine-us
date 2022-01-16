from openfisca_us.model_api import *


class interest_income(Variable):
    value_type = float
    entity = Person
    label = "Interest income"
    unit = USD
    documentation = "Interest income"
    definition_period = YEAR
