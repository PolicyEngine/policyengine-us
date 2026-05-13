from policyengine_us.model_api import *


class selected_marketplace_plan_benchmark_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected marketplace plan premium to benchmark premium ratio"
    unit = "/1"
    definition_period = YEAR
    default_value = 1.0
