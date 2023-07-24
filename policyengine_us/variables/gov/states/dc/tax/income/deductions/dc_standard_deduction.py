from policyengine_us.model_api import *


class dc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    adds = ["basic_standard_deduction", "additional_standard_deduction"]
