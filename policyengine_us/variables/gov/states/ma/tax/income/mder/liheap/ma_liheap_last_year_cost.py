from policyengine_us.model_api import *

class last_year_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Last year's HECS cost"
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-and-benefit-chart-january-2025/download "
