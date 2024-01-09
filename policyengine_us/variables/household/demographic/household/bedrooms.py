from policyengine_us.model_api import *


class bedrooms(Variable):
    value_type = int
    entity = Household
    label = "Bedrooms"
    definition_period = YEAR
