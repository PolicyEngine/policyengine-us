from policyengine_us.model_api import *


class wv_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
