from openfisca_us.model_api import *


class capital_loss(Variable):
    value_type = float
    entity = Person
    label = "Capital loss"
    unit = USD
    documentation = "Losses from transactions involving property."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        capital_gains = tax_unit("capital_gains", period)
        return max_(0, -capital_gains)
