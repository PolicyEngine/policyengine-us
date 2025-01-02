from policyengine_us.model_api import *


class living_arrangements_allow_for_food_preparation(Variable):
    value_type = bool
    entity = Household
    label = "Living arrangements allow for food preparation"
    definition_period = YEAR
