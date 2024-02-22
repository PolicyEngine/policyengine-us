from policyengine_us.model_api import *


class able_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "ABLE contributions"
    unit = USD
    definition_period = YEAR
