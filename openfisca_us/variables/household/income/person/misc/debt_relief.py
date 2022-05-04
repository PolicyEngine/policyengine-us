from openfisca_us.model_api import *


class debt_relief(Variable):
    value_type = float
    entity = Person
    label = "Debt relief income"
    unit = USD
    documentation = "Income from discharge of indebtedness."
    definition_period = YEAR
