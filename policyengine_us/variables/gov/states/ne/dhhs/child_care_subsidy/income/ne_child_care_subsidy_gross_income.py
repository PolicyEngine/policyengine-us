from policyengine_us.model_api import *


class ne_child_care_subsidy_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Nebraska Child Care Subsidy gross program income"
    defined_for = StateCode.NE
    adds = [
        "ne_child_care_subsidy_gross_earned_income",
        "ne_child_care_subsidy_gross_unearned_income",
    ]
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=3",
    )
