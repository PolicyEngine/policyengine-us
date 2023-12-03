from policyengine_us.model_api import *


class ky_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky itemized deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
