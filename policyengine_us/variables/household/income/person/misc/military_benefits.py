from policyengine_us.model_api import *


class military_benefits(Variable):
    value_type = float
    entity = Person
    label = "Military benefits"
    unit = USD
    definition_period = YEAR
