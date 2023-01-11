from policyengine_us.model_api import *


class phone_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Phone expense"
    unit = USD
    definition_period = YEAR

    adds = ["phone_cost"]  # For compatibility
