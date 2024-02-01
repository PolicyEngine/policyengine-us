from policyengine_us.model_api import *


class is_aca_eshi_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for employer-sponsored health insurance "
        "under ACA rules"
    )
    definition_period = YEAR
    default_value = False
