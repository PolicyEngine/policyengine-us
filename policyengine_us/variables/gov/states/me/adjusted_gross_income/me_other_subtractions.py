from policyengine_us.model_api import *


class me_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME other deductions"
    unit = USD
    definition_period = YEAR
    documentation = "Other subtractions available in Maine, shown as Line except 1,3,4 in the below reference"
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"
