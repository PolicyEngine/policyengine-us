from openfisca_us.model_api import *


class unemployment_insurance(Variable):
    value_type = float
    entity = Person
    label = "Unemployment insurance"
    unit = USD
    documentation = "Income from unemployment insurance programs."
    definition_period = YEAR

