from policyengine_us.model_api import *


class occupation(Variable):
    # will add more specific categorical logic after loading variable into CPS
    value_type = int
    entity = Person
    label = "Occupation"
    definition_period = YEAR
