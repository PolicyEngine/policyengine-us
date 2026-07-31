from policyengine_us.model_api import *


class ne_child_care_subsidy_earned_income_disregard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy earned income disregard status"
    defined_for = StateCode.NE
    reference = (
        "https://nebraskalegislature.gov/FloorDocs/109/PDF/Slip/LB304.pdf#page=1",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=35",
    )
