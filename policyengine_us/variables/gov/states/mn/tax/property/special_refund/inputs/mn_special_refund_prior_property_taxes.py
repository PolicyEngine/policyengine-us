from policyengine_us.model_api import *


class mn_special_refund_prior_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund prior qualified taxes before home-use adjustments"
    unit = USD
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses line 2, 2025 column, of the 2026 statement.
    # Enter zero only for a known blank/zero field; -1 means unknown.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2"
