from policyengine_us.model_api import *


class ne_child_care_subsidy_transportation_occurrences(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy approved transportation occurrences"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf#page=1",
    )
