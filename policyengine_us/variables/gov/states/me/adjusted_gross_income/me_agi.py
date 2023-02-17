from policyengine_us.model_api import *


class me_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
