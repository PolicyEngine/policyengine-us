from policyengine_us.model_api import *


class gambling_winnings(Variable):
    value_type = float
    entity = Person
    label = "Gambling winnings"
    unit = USD
    definition_period = YEAR
