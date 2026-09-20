from policyengine_us.model_api import *


class in_ccdf_has_active_under_18_award(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Has an active Indiana CCDF award determined before age 18"
    defined_for = StateCode.IN
    documentation = (
        "Whether this child is continuing an active CCDF award for documented "
        "special needs or court-ordered supervision whose most recent application "
        "or reapplication was approved before age 18. Do not set this from "
        "another household member's enrollment or for a new application at age "
        "18."
    )
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=12"
    )
