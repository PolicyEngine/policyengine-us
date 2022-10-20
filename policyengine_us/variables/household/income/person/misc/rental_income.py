from policyengine_us.model_api import *


class rental_income(Variable):
    value_type = float
    entity = Person
    label = "Rental income"
    unit = USD
    definition_period = YEAR
