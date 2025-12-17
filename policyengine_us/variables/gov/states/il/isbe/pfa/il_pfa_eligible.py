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
    # PFA and PFAE share identical eligibility criteria. The difference is
    # service level: PFA provides half-day, PFAE provides full-day programs.
    # A child receives one or the other based on local program availability,
    # not both simultaneously.
    adds = ["il_pfae_eligible"]
