from policyengine_us.model_api import *

class slspc_age_adjusted_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost adjusted for age"
    unit = USD
    definition_period = MONTH

    adds = ["slspc_age_adjusted_cost_person"]
