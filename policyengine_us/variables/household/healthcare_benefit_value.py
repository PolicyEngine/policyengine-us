from policyengine_us.model_api import *


class healthcare_benefit_value(Variable):
    value_type = float
    label = "Cash equivalent of health coverage"
    entity = Household
    definition_period = YEAR
    unit = USD
    adds = ["medicaid_cost", "per_capita_chip", "aca_ptc"]
