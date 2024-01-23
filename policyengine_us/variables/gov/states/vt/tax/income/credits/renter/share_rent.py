from policyengine_us.model_api import *


class share_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "The household share rent with others"
    definition_period = YEAR
