from policyengine_us.model_api import *


class is_under_court_supervision(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is under court supervision"
    documentation = (
        "Whether this person is under court-ordered supervision. This status "
        "does not by itself indicate a disability, receipt of protective "
        "services, or a court order specifically requiring child care."
    )
    reference = "https://www.ecfr.gov/current/title-45/section-98.20#p-98.20(a)(1)(ii)"
