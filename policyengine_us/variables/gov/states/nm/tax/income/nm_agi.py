from policyengine_us.model_api import *


class nm_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
