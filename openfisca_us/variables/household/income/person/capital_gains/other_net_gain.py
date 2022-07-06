from openfisca_us.model_api import *


class other_net_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Other net gains"
    unit = USD
    documentation = "Other net gain/loss from Form 4797"
    definition_period = YEAR
