from policyengine_us.model_api import *


class nh_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire total exemption allowance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    adds = [
        "nh_base_exemption",
        "nh_blind_exemption",
        "nh_disabled_exemption",
        "nh_old_age_exemption",
    ]
