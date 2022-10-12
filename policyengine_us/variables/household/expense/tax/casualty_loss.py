from policyengine_us.model_api import *


class casualty_loss(Variable):
    value_type = float
    entity = Person
    label = "Casualty/theft loss"
    unit = USD
    definition_period = YEAR
