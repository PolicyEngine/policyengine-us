from policyengine_us.model_api import *


class cost_of_attending_college(Variable):
    value_type = float
    entity = Person
    label = "Cost of college attendance"
    definition_period = YEAR
