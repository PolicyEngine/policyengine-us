from policyengine_us.model_api import *


class ca_la_life_program_eligible(Variable):
    value_type = float
    entity = Person
    label = "LA metro LIFE program eligibility"
    definition_period = YEAR
    defined_for = "in_la"

    adds = [
        "is_snap_eligible",
        "social_security",
        "social_security_disability",
        "is_tanf_eligible",
    ]
