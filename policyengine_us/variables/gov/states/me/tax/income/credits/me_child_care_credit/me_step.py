from policyengine_us.model_api import *


class me_step(Variable):
    value_type = int
    entity = TaxUnit
    label = "ME Child Care Step"
    documentation = "Step child care qualified for"
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf"  # (y)
    default_value = 1
