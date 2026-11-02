from policyengine_us.model_api import *


class social_security_survivors_worker_eligibility_year(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security survivors worker eligibility year"
    documentation = "Explicit underlying-worker eligibility or computation year; zero means unavailable."
