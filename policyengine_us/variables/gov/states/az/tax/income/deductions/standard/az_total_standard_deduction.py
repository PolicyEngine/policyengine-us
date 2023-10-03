from policyengine_us.model_api import *


class az_total_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona total standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = [
        "az_standard_deduction",
        "az_increased_standard_deduction",
    ]
