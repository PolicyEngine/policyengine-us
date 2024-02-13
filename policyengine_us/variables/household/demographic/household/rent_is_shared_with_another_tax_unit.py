from policyengine_us.model_api import *


class rent_is_shared_with_another_tax_unit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the household shares rent with others"
    definition_period = YEAR
