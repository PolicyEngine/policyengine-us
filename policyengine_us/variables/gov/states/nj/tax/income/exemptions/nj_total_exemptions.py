from policyengine_us.model_api import *


class nj_total_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey total exemption allowance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    adds = [
        "nj_regular_exemption",
        "nj_senior_exemption",
        "nj_dependents_exemption",
        "nj_blind_or_disabled_exemption",
        "nj_dependents_attending_college_exemption",
    ]
