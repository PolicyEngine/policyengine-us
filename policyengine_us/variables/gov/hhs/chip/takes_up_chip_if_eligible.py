from policyengine_us.model_api import *


class takes_up_chip_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether a random eligible person enrolls in CHIP"
    definition_period = YEAR

    def formula(person, period, parameters):
        seed = person("chip_take_up_seed", period)
        takeup_rate = parameters(period).gov.hhs.chip.takeup_rate
        return seed < takeup_rate
