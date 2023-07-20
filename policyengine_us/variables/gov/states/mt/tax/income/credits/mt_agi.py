from policyengine_us.model_api import *


class mt_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana adjusted gross income"
    defined_for = StateCode.MT
    unit = USD
    definition_period = YEAR
