from policyengine_us.model_api import *


class tax_unit_stillborn_parent(Variable):
    value_type = int
    entity = TaxUnit
    label = (
        "Head or spouse is the parent of a stillborn child in the filing year"
    )
    definition_period = YEAR
