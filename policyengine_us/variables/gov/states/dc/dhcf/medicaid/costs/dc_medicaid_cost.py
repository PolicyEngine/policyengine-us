from policyengine_us.model_api import *


class dc_medicaid_cost(Variable):
    value_type = float
    entity = Person
    label = "DC Medicaid/Alliance cost"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_medicaid_enrolled"
    adds = ["dc_medicaid_cost_if_enrolled"]