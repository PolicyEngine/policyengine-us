from policyengine_us.model_api import *


class health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Person-level health insurance premiums supplied directly as an "
        "input. Program-specific medical expense variables should use explicit "
        "premium components where available."
    )
