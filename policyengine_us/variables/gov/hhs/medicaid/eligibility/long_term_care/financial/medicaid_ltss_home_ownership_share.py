from policyengine_us.model_api import *


class medicaid_ltss_home_ownership_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS home ownership share"
    unit = "/1"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit fractional share of the home's equity owned by the LTSS "
        "applicant, from zero to one. Zero is the safe default. The model does "
        "not determine title, jointly owned shares, or legal ownership."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f"
