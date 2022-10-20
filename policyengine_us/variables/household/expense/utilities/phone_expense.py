from policyengine_us.model_api import *


class phone_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Phone expense"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["phone_cost"])  # For compatibility
