from policyengine_us.model_api import *


class homeowners_insurance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Homeowners insurance"
    unit = USD
    definition_period = YEAR
