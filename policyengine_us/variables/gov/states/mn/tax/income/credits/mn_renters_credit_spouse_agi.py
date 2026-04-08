from policyengine_us.model_api import *


class mn_renters_credit_spouse_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Spouse AGI for Minnesota renter's credit married-filing-separately cases"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.MN

