from policyengine_us.model_api import *


class mn_special_refund_same_homestead(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota special refund same owner occupied the homestead on both required dates"
    definition_period = YEAR
    # Claim year 2025 requires ownership and occupancy on January 2, 2025 and 2026.
    reference = "https://www.revisor.mn.gov/statutes/cite/290A.04#stat.290A.04.2h"
