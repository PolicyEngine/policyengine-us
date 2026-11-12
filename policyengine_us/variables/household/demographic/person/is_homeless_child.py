from policyengine_us.model_api import *


class is_homeless_child(Variable):
    value_type = bool
    entity = Person
    default_value = False
    label = "Child qualifies as homeless for school meals"
    definition_period = YEAR
    documentation = (
        "Whether a school liaison, shelter director or other authorized "
        "official has identified this child as homeless under the "
        "McKinney-Vento definition for school meal certification. This input "
        "can identify one child when the whole household is not homeless."
    )
    reference = (
        "https://www.ecfr.gov/current/title-7/section-245.2",
        "https://www.law.cornell.edu/uscode/text/42/1758#b_12_A_iv",
    )
