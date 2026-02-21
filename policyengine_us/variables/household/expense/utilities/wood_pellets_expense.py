from policyengine_us.model_api import *


class wood_pellets_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wood pellets expense"
    unit = USD
    definition_period = YEAR
