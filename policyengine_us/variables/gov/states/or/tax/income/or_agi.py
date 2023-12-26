from policyengine_us.model_api import *


class or_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
