from policyengine_us.model_api import *


class capital_losses(Variable):
    value_type = float
    entity = Person
    label = "Capital losses (expressed as a non-negative number)"
    unit = USD
    documentation = "Losses from transactions involving property."
    definition_period = YEAR

    def formula(person, period, parameters):
        return max_(0, -person("capital_gains", period))
