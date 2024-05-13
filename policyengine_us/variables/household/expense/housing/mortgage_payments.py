from policyengine_us.model_api import *


class mortgage_payments(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mortgage payments"
    unit = USD
    definition_period = YEAR
