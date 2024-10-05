from policyengine_us.model_api import *


class strike_benefits(Variable):
    value_type = float
    entity = Person
    label = "strike benefits"
    unit = USD
    definition_period = YEAR
