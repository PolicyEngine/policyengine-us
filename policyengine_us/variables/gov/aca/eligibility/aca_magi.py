from policyengine_us.model_api import *


class aca_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "ACA-related modified AGI for this tax unit"
    definition_period = YEAR
    adds = ["medicaid_magi"]
