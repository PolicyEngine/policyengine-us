from policyengine_us.model_api import *


class mn_special_refund_current_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Minnesota special refund current qualified taxes before home-use adjustments"
    )
    unit = USD
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses the 2026 statement's line 1 or qualified worksheet amount.
    # This input is before home-use and improvement adjustments; -1 means unknown.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=1"
