from policyengine_us.model_api import *


class self_employment_tax(Variable):
    value_type = float
    entity = Person
    label = "self-employment tax"
    definition_period = YEAR
    unit = USD
    adds = [
        "self_employment_social_security_tax",
        "self_employment_medicare_tax",
    ]
