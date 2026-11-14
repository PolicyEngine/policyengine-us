from policyengine_us.model_api import *


class mn_special_refund_prior_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund actual prior-year special refund"
    unit = USD
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses corrected 2024 M1PR line 15, not the regular refund.
    # Enter zero when no prior special refund was received; -1 means unknown.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2"
