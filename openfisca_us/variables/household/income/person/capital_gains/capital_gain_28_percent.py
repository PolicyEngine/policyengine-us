from openfisca_us.model_api import *


class capital_gain_28_percent(Variable):
    value_type = float
    entity = TaxUnit
    label = "28\% rate gain"
    unit = USD
    definition_period = YEAR
