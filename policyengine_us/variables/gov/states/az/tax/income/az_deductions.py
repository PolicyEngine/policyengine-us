from policyengine_us.model_api import *


class az_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ