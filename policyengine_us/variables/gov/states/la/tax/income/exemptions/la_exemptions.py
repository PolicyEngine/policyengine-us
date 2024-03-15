from policyengine_us.model_api import *


class la_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA
    adds = [
        "la_personal_exemption",
        "la_blind_exemption",
        "la_dependents_exemption",
        "la_widow_exemption",
        "la_aged_exemption",
    ]
