from policyengine_us.model_api import *


class tax_unit_disabled_veteran(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of disabled veterans in the tax unit"
    definition_period = YEAR
