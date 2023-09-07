from policyengine_us.model_api import *


class nc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina itemized deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
