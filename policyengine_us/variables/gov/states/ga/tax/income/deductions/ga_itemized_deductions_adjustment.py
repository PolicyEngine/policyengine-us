from policyengine_us.model_api import *


class ga_itemized_deductions_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia itemized deductions adjustment"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.GA
