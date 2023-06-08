from policyengine_us.model_api import *


class la_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana total exemption allowance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA
    adds = [
        "la_aged_exemption",
        "la_blind_or_disabled_exemption",
        "la_dependents_exemption",
        "la_personal_exemption",
    ]
