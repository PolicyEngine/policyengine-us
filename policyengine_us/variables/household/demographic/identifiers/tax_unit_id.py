from policyengine_us.model_api import *


class tax_unit_id(Variable):
    value_type = int
    entity = TaxUnit
    label = "Unique reference for this tax unit"
    definition_period = YEAR
