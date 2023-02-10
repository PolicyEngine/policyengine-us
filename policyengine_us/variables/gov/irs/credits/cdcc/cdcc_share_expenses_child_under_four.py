from policyengine_us.model_api import *


class cdcc_share_expenses_child_under_four(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expenses"
    unit = USD
    definition_period = YEAR
