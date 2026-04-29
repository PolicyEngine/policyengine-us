from policyengine_us.model_api import *


class chip_take_up_seed(Variable):
    value_type = float
    entity = Person
    label = "Randomly assigned seed for CHIP take-up"
    definition_period = YEAR
