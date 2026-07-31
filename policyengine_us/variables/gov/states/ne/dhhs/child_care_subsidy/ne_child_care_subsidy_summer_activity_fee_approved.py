from policyengine_us.model_api import *


class ne_child_care_subsidy_summer_activity_fee_approved(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy summer activity fee approved"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=9",
    )
