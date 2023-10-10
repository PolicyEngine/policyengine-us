from policyengine_us.model_api import *


class mt_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Adjusted Gross Income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
