from policyengine_us.model_api import *


class free_school_meals_reported(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Free school meals (reported)"
    unit = USD
