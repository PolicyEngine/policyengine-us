from policyengine_us.model_api import *


class selected_marketplace_plan_premium_proxy(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected marketplace plan premium proxy"
    unit = USD
    definition_period = YEAR
    adds = ["monthly_selected_marketplace_plan_premium_proxy"]
