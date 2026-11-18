from policyengine_us.model_api import *


class social_security_disability_worker_eligibility_year(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = "Social Security disability worker eligibility year"
    documentation = "Explicit underlying-worker eligibility or computation year; zero means unavailable."
