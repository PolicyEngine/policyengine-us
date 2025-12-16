from policyengine_us.model_api import *


class il_pfa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Preschool For All (PFA)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf",
    )
    defined_for = StateCode.IL
    # PFA and PFAE have the same child eligibility criteria in practice.
    # The difference is the level of service: PFA is half-day, PFAE is full-day.
    # Whether a child gets PFA vs PFAE depends on program availability in their area.
    adds = ["il_pfae_eligible"]
