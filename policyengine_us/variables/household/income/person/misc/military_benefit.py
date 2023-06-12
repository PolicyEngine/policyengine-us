from policyengine_us.model_api import *


class military_benefit(Variable):
    value_type = float
    entity = Person
    label = "Military benefit"
    unit = USD
    definition_period = YEAR
