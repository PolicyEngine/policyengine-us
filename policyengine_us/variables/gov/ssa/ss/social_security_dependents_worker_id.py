from policyengine_us.model_api import *


class social_security_dependents_worker_id(Variable):
    value_type = str
    default_value = ""
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents worker id"
    documentation = "Underlying-worker person identifier; requires an explicit computation year on that record."
