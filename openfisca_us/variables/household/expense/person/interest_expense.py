from openfisca_us.model_api import *


class interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on loans"
    unit = USD
    definition_period = YEAR
