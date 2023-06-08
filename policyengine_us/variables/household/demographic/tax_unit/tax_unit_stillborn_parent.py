from policyengine_us.model_api import *


class tax_unit_stillborn_parent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Is the parent of a stillborn child"
    definition_period = YEAR
