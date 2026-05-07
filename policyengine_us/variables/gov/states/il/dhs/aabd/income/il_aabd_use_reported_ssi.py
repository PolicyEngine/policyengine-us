from policyengine_us.model_api import *


class il_aabd_use_reported_ssi(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    default_value = False
    label = "Use reported SSI for IL AABD calculation"
    documentation = (
        "When True, IL AABD uses ssi_reported instead of calculated ssi "
        "as unearned income. This allows API partners to show both federal "
        "SSI entitlement and IL AABD eligibility in a single response."
    )
