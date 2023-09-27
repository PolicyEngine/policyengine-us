from policyengine_us.model_api import *


class ga_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
