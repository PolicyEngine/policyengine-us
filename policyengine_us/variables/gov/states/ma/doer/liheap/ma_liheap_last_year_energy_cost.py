from policyengine_us.model_api import *


class ma_liheap_last_year_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Massachusetts LIHEAP last year's energy cost"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-and-benefit-chart-january-2025/download"
