from policyengine_us.model_api import *


class heating_expense_last_year(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Household's heating expense last year"
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"
