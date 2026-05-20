from policyengine_us.model_api import *


class selected_marketplace_plan_benchmark_ratio(Variable):
    value_type = float
    entity = TaxUnit
    label = "Selected marketplace plan premium to benchmark premium ratio"
    unit = "/1"
    definition_period = YEAR
    default_value = 1.0
    documentation = (
        "Ratio of the selected Marketplace plan gross premium to the second "
        "lowest cost silver plan benchmark premium. This is an explicit "
        "user- or data-supplied input; when absent, the model assumes the "
        "selected plan premium equals the benchmark premium."
    )
