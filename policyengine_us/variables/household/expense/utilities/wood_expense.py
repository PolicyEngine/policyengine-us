from policyengine_us.model_api import *


class wood_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wood expense"
    unit = USD
    definition_period = YEAR
    documentation = "Annual expense for wood or wood pellet heating fuel."
