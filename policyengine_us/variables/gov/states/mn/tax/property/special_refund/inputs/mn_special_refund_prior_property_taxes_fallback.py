from policyengine_us.model_api import *


class mn_special_refund_prior_property_taxes_fallback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota special refund prior taxes from the alternative statement field"
    unit = USD
    definition_period = YEAR
    default_value = -1
    # Claim year 2025 uses line 5, 2025 column, of the 2026 statement, only when
    # the prior-tax line 2 is known blank/zero. This is not an imputed tax bill.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2"
