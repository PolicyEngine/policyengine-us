from policyengine_us.model_api import *


class home_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "home mortgage interest"
    unit = USD
    definition_period = YEAR
