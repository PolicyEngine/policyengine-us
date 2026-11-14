from policyengine_us.model_api import *


class mn_special_refund_taxable_market_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund current taxable market value"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses Worksheet 3 step 2, the 2026 statement's taxable value.
    # Required only when new improvements or expired exclusions are positive.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=12"
