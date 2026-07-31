from policyengine_us.model_api import *


class ne_child_care_subsidy_special_needs_rate_approved(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy special-needs rate approved"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=10",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=51",
    )
