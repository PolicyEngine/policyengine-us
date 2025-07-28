from policyengine_us.model_api import *


class household_count(Variable):
    value_type = float
    entity = Household
    label = "Households represented"
    definition_period = YEAR
    default_value = 1.0
