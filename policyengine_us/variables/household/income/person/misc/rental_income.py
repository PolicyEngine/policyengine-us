from policyengine_us.model_api import *


class rental_income(Variable):
    value_type = float
    entity = Person
    label = "rental income"
    documentation = "Income from rental of property"
    unit = USD
    definition_period = YEAR
