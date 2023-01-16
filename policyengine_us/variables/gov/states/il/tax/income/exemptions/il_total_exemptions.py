from policyengine_us.model_api import *


class il_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL total exemption allowance"
    unit = USD
    definition_period = YEAR

    defined_for = "il_is_exemption_eligible"

    adds = [
        "il_personal_exemption",
        "il_aged_blind_exemption",
        "il_dependent_exemption",
    ]
