from policyengine_us.model_api import *


class rent_is_subsidized(Variable):
    value_type = bool
    entity = TaxUnit
    label = "The household received subsidies"
    definition_period = YEAR
