from policyengine_us.model_api import *


class tax_unit_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax units represented"
    definition_period = YEAR
    default_value = 1.0
