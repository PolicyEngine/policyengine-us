from policyengine_us.model_api import *


class rent_is_subsidized(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the rent of this household is subsidied"
    definition_period = YEAR
