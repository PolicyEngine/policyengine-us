from policyengine_us.model_api import *


class il_pi_priority_score(Variable):
    value_type = int
    entity = Person
    label = "Weighted priority score for Illinois PI eligibility"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=2",
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=3",
    )
    defined_for = "il_pi_demographic_eligible"

    adds = [
        "il_pi_highest_priority_score",
        "il_pi_other_priority_score",
        "il_pi_lower_priority_score",
    ]
