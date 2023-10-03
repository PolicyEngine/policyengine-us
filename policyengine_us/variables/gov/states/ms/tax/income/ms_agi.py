from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS
