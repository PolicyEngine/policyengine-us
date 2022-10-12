from policyengine_us.model_api import *


class social_security_reported(Variable):
    value_type = float
    entity = Person
    label = "Social Security (reported)"
    unit = USD
    definition_period = YEAR
