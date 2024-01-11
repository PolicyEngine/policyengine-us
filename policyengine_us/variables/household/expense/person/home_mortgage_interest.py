from policyengine_us.model_api import *


class home_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on a home mortgage"
    unit = USD
    definition_period = YEAR
    documentation = "Home mortgage interest, including both reported and not reported on federal Form 1098."
