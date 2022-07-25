from openfisca_us.model_api import *


class in_other_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN other taxes"
    unit = USD
    definition_period = YEAR
    documentation = "Includes the use tax on out-of-state purchases, household employment taxes, and recapture of certain Indiana offset credits."
