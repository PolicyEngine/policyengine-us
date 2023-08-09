from policyengine_us.model_api import *


class cost_of_tuition(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant cost of attendance"
    definition_period = YEAR
