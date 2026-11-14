from policyengine_us.model_api import *


class mn_special_refund_prior_home_use_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund prior-year fraction used as a home"
    unit = "/1"
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses the 2024 personal-home share.
    # Enter 1 for a wholly personal home; -1 means unknown.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2"
