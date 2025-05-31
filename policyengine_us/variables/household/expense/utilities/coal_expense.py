from policyengine_us.model_api import *


class coal_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Coal expense"
    unit = USD
    definition_period = YEAR
