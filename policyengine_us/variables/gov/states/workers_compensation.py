from policyengine_us.model_api import *


class workers_compensation(Variable):
    value_type = float
    entity = Person
    label = "worker's compensation"
    unit = USD
    definition_period = YEAR
