from policyengine_us.model_api import *


class tax_unit_is_dependent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Is a dependent on someone else’s return"
    definition_period = YEAR
