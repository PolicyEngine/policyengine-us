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
        "identifies one child when the whole household is not homeless; "
        "is_homeless covers a household without a fixed nighttime residence."
    )
    reference = (
        "https://www.ecfr.gov/current/title-7/section-245.2",
        "https://uscode.house.gov/us/usc/119-124/t42/s1758/#b-12-A-iv",
        "https://uscode.house.gov/us/usc/119-124/t42/s11434a/#2",
    )
