from policyengine_us.model_api import *


class mn_special_refund_improvement_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund value of new improvements and expired exclusions"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses Worksheet 3 step 1 from the 2026 property tax statement.
    # Enter zero when there were none; -1 means unknown.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-06/m1pr-inst-25.pdf#page=12"
