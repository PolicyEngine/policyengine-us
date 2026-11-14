from policyengine_us.model_api import *


class mn_special_refund_disabled_veteran_exclusion(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota special refund claimant received the disabled-veteran homestead exclusion"
    definition_period = YEAR
    # Permits actual zero prior taxes only when both statement fields are known zero.
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1prsr-25.pdf#page=2"
