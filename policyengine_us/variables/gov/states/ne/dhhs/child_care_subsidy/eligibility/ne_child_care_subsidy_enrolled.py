from policyengine_us.model_api import *


class ne_child_care_subsidy_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in the Nebraska Child Care Subsidy program"
    documentation = "This input variable defaults to false, so microsimulation runs model no continuing recipients: the LB304 earned income disregard, the 85% SMI current-period exit limit, and the enrolled activity and asset continuity never apply, biasing modeled eligibility toward the 185% FPG initial-entry tier."
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=31",
    )
