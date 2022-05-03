from openfisca_us.model_api import *


class dsi(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Dependent elsewhere"
    documentation = "Claimed as dependent in another tax unit"
