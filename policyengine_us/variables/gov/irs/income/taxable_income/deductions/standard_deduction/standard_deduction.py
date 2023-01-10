from policyengine_us.model_api import *


class standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/63#c"

    adds = ["basic_standard_deduction", "additional_standard_deduction"]
