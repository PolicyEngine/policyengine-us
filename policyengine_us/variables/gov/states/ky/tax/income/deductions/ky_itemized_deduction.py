from policyengine_us.model_api import *


class ky_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
