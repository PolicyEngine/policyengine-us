from policyengine_us.model_api import *


class hi_child_support_received(Variable):
    value_type = float
    entity = Person
    label = "Child receiving support"
    definition_period = YEAR
