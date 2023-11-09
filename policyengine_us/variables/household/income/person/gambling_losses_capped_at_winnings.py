from policyengine_us.model_api import *


class gambling_losses_capped_at_winnings(Variable):
    value_type = float
    entity = Person
    label = "Gambling losses up to winnings"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        gambling_losses = person("gambling_losses", period)
        gambling_winnings = person("gambling_winnings", period)
        return min_(gambling_losses, gambling_winnings)
