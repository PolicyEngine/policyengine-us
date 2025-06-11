from policyengine_us.model_api import *


class medicaid_take_up_seed(Variable):
    value_type = float
    entity = Person
    label = "Randomly assigned seed for Medicaid take-up"
    definition_period = YEAR
