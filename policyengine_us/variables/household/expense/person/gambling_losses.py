from policyengine_us.model_api import *


class gambling_losses(Variable):
    value_type = float
    entity = Person
    label = "Gambling losses up to gambling winnings"
    unit = USD
    definition_period = YEAR
